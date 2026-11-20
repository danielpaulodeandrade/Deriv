import asyncio
import json
import logging
from contextlib import suppress
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

from websockets.asyncio.client import connect

from app.core.config import settings
from app.db.connection import get_db_pool
from app.services.candle_builder import CandleBuilder

logger = logging.getLogger(__name__)


class DerivMarketData:
    HISTORY_PAGE_SIZE = 5000
    HISTORY_REQUEST_ID = 9000
    HISTORY_DAYS = 14
    GRANULARITY_SECONDS = 60
    STALE_AFTER_SECONDS = 10
    PERSISTENCE_STALE_AFTER_SECONDS = 90

    def __init__(self):
        self.symbols = list(
            dict.fromkeys(
                symbol.strip()
                for symbol in settings.DERIV_SYMBOLS.split(",")
                if symbol.strip()
            )
        )
        self._stop = asyncio.Event()
        self._queue = asyncio.Queue(maxsize=50000)
        self._candle_builder = CandleBuilder()
        self._connection = None
        self._consumer_task = None
        self._writer_task = None
        self._recovery_task = None
        self._lifecycle_lock = asyncio.Lock()
        self._connected = False
        self._connected_at = None
        self._last_tick_received_at = {}
        self._last_tick_epoch = {}
        self._received_ticks = 0
        self._recovered_candles = 0
        self._write_batches = 0
        self._write_items = 0
        self._db_errors = 0
        self._connection_errors = 0
        self._gap_events = 0
        self._last_db_success_at = None
        self._last_error = None
        self._started_at = datetime.now(timezone.utc)

    async def start(self):
        async with self._lifecycle_lock:
            if not self.symbols:
                logger.warning("No Deriv symbols configured. Market data disabled.")
                return

            writer_running = self._writer_task is not None and not self._writer_task.done()
            consumer_running = self._consumer_task is not None and not self._consumer_task.done()
            if writer_running and consumer_running:
                logger.warning("Deriv market data service is already running.")
                return
            if writer_running or consumer_running:
                raise RuntimeError(
                    "Deriv market data service is in a partial state. Call stop() before starting it again."
                )

            self._stop.clear()
            self._started_at = datetime.now(timezone.utc)
            self._writer_task = asyncio.create_task(
                self._database_writer(), name="deriv-candle-writer"
            )
            try:
                self._consumer_task = asyncio.create_task(
                    self._consume_ticks(), name="deriv-tick-consumer"
                )
            except Exception:
                self._stop.set()
                await self._writer_task
                self._writer_task = None
                raise

            logger.info("Deriv market data service started: %s", self.symbols)

    async def stop(self):
        async with self._lifecycle_lock:
            self._stop.set()
            connection = self._connection
            if connection is not None:
                try:
                    await connection.close()
                except Exception:
                    logger.exception("Error while closing Deriv WebSocket.")

            consumer_task = self._consumer_task
            try:
                if consumer_task is not None:
                    await consumer_task
            finally:
                await self._cancel_recovery_task()
                writer_task = self._writer_task
                if writer_task is not None:
                    # Do not cancel the writer: it may own an uncommitted batch.
                    await writer_task
                self._connection = None
                self._connected = False
                self._consumer_task = None
                self._writer_task = None
                self._recovery_task = None
                self._candle_builder.reset()

            logger.info("Deriv market data service stopped.")

    async def _cancel_recovery_task(self):
        recovery_task = self._recovery_task
        self._recovery_task = None
        if (
            recovery_task is not None
            and recovery_task is not asyncio.current_task()
            and not recovery_task.done()
        ):
            recovery_task.cancel()
            with suppress(asyncio.CancelledError):
                await recovery_task

    async def _consume_ticks(self):
        delay = settings.DERIV_RECONNECT_DELAY_SECONDS
        try:
            while not self._stop.is_set():
                try:
                    logger.info("Connecting to Deriv public WebSocket.")
                    async with connect(
                        settings.DERIV_WS_URL,
                        ping_interval=20,
                        ping_timeout=20,
                        close_timeout=5,
                    ) as ws:
                        self._connection = ws
                        self._connected = True
                        self._connected_at = datetime.now(timezone.utc)
                        self._last_error = None
                        delay = settings.DERIV_RECONNECT_DELAY_SECONDS
                        self._candle_builder.reset()
                        logger.info("Connected to Deriv WebSocket.")

                        await self._cancel_recovery_task()
                        if self._stop.is_set():
                            break

                        # Read persisted cursors before live subscriptions, so live
                        # writes cannot conceal a gap from the history recovery.
                        recovery_cursors = {}
                        for symbol in self.symbols:
                            if self._stop.is_set():
                                break
                            recovery_cursors[symbol] = (
                                await self._last_persisted_candle_epoch(symbol)
                            )
                        if self._stop.is_set():
                            break

                        # Subscribe first; recovery runs on a separate connection.
                        for req_id, symbol in enumerate(self.symbols, start=1):
                            if self._stop.is_set():
                                break
                            await ws.send(
                                json.dumps(
                                    {"ticks": symbol, "subscribe": 1, "req_id": req_id}
                                )
                            )
                            logger.info("Subscribed to ticks: %s", symbol)

                        if self._stop.is_set():
                            break

                        self._recovery_task = asyncio.create_task(
                            self._recover_missing_candles(recovery_cursors),
                            name="deriv-candle-recovery",
                        )

                        async for raw_message in ws:
                            if self._stop.is_set():
                                break
                            await self._process_message(raw_message)

                        self._connection = None
                        self._connected = False
                        self._candle_builder.reset()
                        if not self._stop.is_set():
                            raise ConnectionError("Deriv WebSocket disconnected.")

                except asyncio.CancelledError:
                    raise
                except Exception:
                    self._connection = None
                    self._connected = False
                    self._candle_builder.reset()
                    if self._stop.is_set():
                        break
                    self._connection_errors += 1
                    self._last_error = "WebSocket connection failure"
                    logger.exception(
                        "Deriv connection failed. Reconnecting in %.1f seconds.", delay
                    )
                    try:
                        await asyncio.wait_for(self._stop.wait(), timeout=delay)
                    except asyncio.TimeoutError:
                        pass
                    delay = min(delay * 2, 60)
        finally:
            self._connection = None
            self._connected = False
            self._candle_builder.reset()
            await self._cancel_recovery_task()

    async def _process_message(self, raw_message: str):
        try:
            message = json.loads(raw_message)
            if "error" in message:
                logger.error("Deriv API error: %s", message["error"])
                return
            if message.get("msg_type") != "tick":
                return

            tick = message.get("tick") or {}
            symbol = tick.get("symbol")
            epoch_value = tick.get("epoch")
            quote = tick.get("quote")
            if not symbol or epoch_value is None or quote is None:
                logger.warning("Incomplete tick received: %s", message)
                return
            if symbol not in self.symbols:
                logger.warning("Unexpected symbol received: %s", symbol)
                return

            epoch = int(epoch_value)
            price = Decimal(str(quote))
            if not price.is_finite() or price <= 0:
                raise ValueError("Tick price must be finite and positive.")

            previous_epoch = self._last_tick_epoch.get(symbol)
            if previous_epoch is not None and epoch > previous_epoch:
                if epoch - previous_epoch > 5:
                    self._gap_events += 1
            self._last_tick_epoch[symbol] = max(epoch, previous_epoch or epoch)
            self._last_tick_received_at[symbol] = datetime.now(timezone.utc)
            self._received_ticks += 1

            completed = self._candle_builder.update(symbol, epoch, price)
            if completed is not None:
                await self._queue.put(self._candle_queue_item("live", completed))

        except (ValueError, TypeError, InvalidOperation, OverflowError):
            logger.exception("Invalid tick received.")

    @staticmethod
    def _candle_queue_item(source: str, candle):
        return (
            source,
            candle.asset_symbol,
            candle.candle_start,
            candle.open,
            candle.high,
            candle.low,
            candle.close,
        )

    async def _last_persisted_candle_epoch(self, symbol: str):
        pool = get_db_pool()
        if pool is None:
            raise RuntimeError("Database pool unavailable.")
        async with pool.acquire() as conn:
            candle_start = await conn.fetchval(
                """
                SELECT MAX(candle_start)
                FROM price_candles
                WHERE asset_symbol = $1
                """,
                symbol,
            )
        return int(candle_start.timestamp()) if candle_start is not None else None

    async def _request_history(self, ws, symbol: str, start: int, end):
        request = {
            "ticks_history": symbol,
            "start": start,
            "end": end,
            "count": self.HISTORY_PAGE_SIZE,
            "style": "candles",
            "granularity": self.GRANULARITY_SECONDS,
            "adjust_start_time": 1,
            "req_id": self.HISTORY_REQUEST_ID,
        }
        await ws.send(json.dumps(request))

        while not self._stop.is_set():
            raw_message = await asyncio.wait_for(ws.recv(), timeout=30)
            message = json.loads(raw_message)
            if message.get("req_id") != self.HISTORY_REQUEST_ID:
                continue
            if "error" in message:
                raise RuntimeError(f"Candle history error for {symbol}: {message['error']}")
            if message.get("msg_type") != "candles":
                continue
            candles = message.get("candles") or []
            return candles
        return []

    async def _recover_missing_candles(
        self, cursors: dict[str, int | None] | None = None
    ):
        delay = settings.DERIV_RECONNECT_DELAY_SECONDS
        while not self._stop.is_set():
            try:
                async with connect(
                    settings.DERIV_WS_URL,
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=5,
                ) as ws:
                    delay = settings.DERIV_RECONNECT_DELAY_SECONDS
                    for symbol in self.symbols:
                        if self._stop.is_set():
                            break

                        if cursors is None:
                            last_epoch = await self._last_persisted_candle_epoch(symbol)
                        else:
                            last_epoch = cursors.get(symbol)

                        if last_epoch is None:
                            start = int(
                                (datetime.now(timezone.utc) - timedelta(days=self.HISTORY_DAYS))
                                .timestamp()
                            )
                            logger.info(
                                "Initial candle history for %s: last %d days.",
                                symbol,
                                self.HISTORY_DAYS,
                            )
                        else:
                            # Include the last saved candle for safe reconciliation.
                            start = max(0, int(last_epoch) - self.GRANULARITY_SECONDS)
                            logger.info(
                                "Recovering candles for %s from epoch %d.", symbol, start
                            )

                        end = "latest"
                        recovered = 0
                        while not self._stop.is_set():
                            candles = await self._request_history(ws, symbol, start, end)
                            if not candles:
                                break

                            epochs = [int(item["epoch"]) for item in candles]
                            earliest = min(epochs)
                            current_minute = (
                                int(datetime.now(timezone.utc).timestamp())
                                // self.GRANULARITY_SECONDS
                                * self.GRANULARITY_SECONDS
                            )

                            for item in candles:
                                epoch = int(item["epoch"])
                                candle_epoch = (
                                    epoch - epoch % self.GRANULARITY_SECONDS
                                )
                                if candle_epoch < start or candle_epoch >= current_minute:
                                    continue
                                try:
                                    open_price = Decimal(str(item["open"]))
                                    high_price = Decimal(str(item["high"]))
                                    low_price = Decimal(str(item["low"]))
                                    close_price = Decimal(str(item["close"]))
                                except (KeyError, InvalidOperation, TypeError) as exc:
                                    raise ValueError(
                                        f"Invalid candle returned for {symbol}: {item}"
                                    ) from exc

                                values = (open_price, high_price, low_price, close_price)
                                if any(not value.is_finite() or value <= 0 for value in values):
                                    raise ValueError(
                                        f"Invalid OHLC values returned for {symbol}: {item}"
                                    )
                                if (
                                    high_price < max(open_price, close_price, low_price)
                                    or low_price > min(open_price, close_price, high_price)
                                ):
                                    raise ValueError(
                                        f"Inconsistent OHLC values returned for {symbol}: {item}"
                                    )

                                candle_start = datetime.fromtimestamp(
                                    candle_epoch, tz=timezone.utc
                                )
                                await self._queue.put(
                                    (
                                        "history",
                                        symbol,
                                        candle_start,
                                        open_price,
                                        high_price,
                                        low_price,
                                        close_price,
                                    )
                                )
                                recovered += 1
                                self._recovered_candles += 1

                            if earliest <= start or len(candles) < self.HISTORY_PAGE_SIZE:
                                break

                            next_end = earliest - 1
                            if isinstance(end, int) and next_end >= end:
                                logger.warning(
                                    "Candle history pagination made no progress for %s.",
                                    symbol,
                                )
                                break
                            end = next_end

                        logger.info(
                            "Candle history recovery completed for %s: %d candles queued.",
                            symbol,
                            recovered,
                        )
                    return
            except asyncio.CancelledError:
                raise
            except Exception:
                self._last_error = "Candle history recovery failure"
                logger.exception(
                    "Candle history recovery failed. Retrying in %.1f seconds.", delay
                )
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=delay)
                except asyncio.TimeoutError:
                    pass
                delay = min(delay * 2, 60)

    async def _database_writer(self):
        batch_size = settings.DERIV_BATCH_SIZE
        flush_interval = settings.DERIV_FLUSH_INTERVAL_SECONDS

        while not self._stop.is_set() or not self._queue.empty():
            batch = []
            try:
                first = await asyncio.wait_for(
                    self._queue.get(), timeout=flush_interval
                )
                batch.append(first)
            except asyncio.TimeoutError:
                continue

            while len(batch) < batch_size:
                try:
                    batch.append(self._queue.get_nowait())
                except asyncio.QueueEmpty:
                    break

            history_rows = [item[1:] for item in batch if item[0] == "history"]
            live_rows = [item[1:] for item in batch if item[0] == "live"]

            while True:
                pool = get_db_pool()
                if pool is None:
                    logger.error("Database pool unavailable. Retrying candle batch.")
                    await asyncio.sleep(2)
                    continue
                try:
                    async with pool.acquire() as conn:
                        async with conn.transaction():
                            if history_rows:
                                await conn.executemany(
                                    """
                                    INSERT INTO price_candles (
                                        asset_symbol,
                                        candle_start,
                                        open,
                                        high,
                                        low,
                                        close
                                    )
                                    VALUES ($1, $2, $3, $4, $5, $6)
                                    ON CONFLICT (candle_start, asset_symbol)
                                    DO UPDATE SET
                                        open = EXCLUDED.open,
                                        high = EXCLUDED.high,
                                        low = EXCLUDED.low,
                                        close = EXCLUDED.close
                                    """,
                                    history_rows,
                                )
                            if live_rows:
                                await conn.executemany(
                                    """
                                    INSERT INTO price_candles (
                                        asset_symbol,
                                        candle_start,
                                        open,
                                        high,
                                        low,
                                        close
                                    )
                                    VALUES ($1, $2, $3, $4, $5, $6)
                                    ON CONFLICT (candle_start, asset_symbol)
                                    DO NOTHING
                                    """,
                                    live_rows,
                                )

                    self._write_batches += 1
                    self._write_items += len(batch)
                    self._last_db_success_at = datetime.now(timezone.utc)
                    for _ in batch:
                        self._queue.task_done()
                    logger.debug("Persisted %d candles.", len(batch))
                    break
                except asyncio.CancelledError:
                    raise
                except Exception:
                    self._db_errors += 1
                    self._last_error = "Database persistence failure"
                    logger.exception(
                        "Failed to persist %d candles. Retrying.", len(batch)
                    )
                    await asyncio.sleep(2)

    def get_status(self):
        now = datetime.now(timezone.utc)
        stale_assets = []
        assets_status = {}

        for symbol in self.symbols:
            last_received = self._last_tick_received_at.get(symbol)
            last_epoch = self._last_tick_epoch.get(symbol)
            seconds_since = (
                (now - last_received).total_seconds()
                if last_received
                else (now - self._started_at).total_seconds()
            )
            stale = seconds_since > self.STALE_AFTER_SECONDS
            if stale:
                stale_assets.append(symbol)
            assets_status[symbol] = {
                "last_tick_epoch": last_epoch,
                "last_tick_received_at": (
                    last_received.isoformat() if last_received else None
                ),
                "seconds_since_last_tick": round(seconds_since, 2),
                "stale": stale,
            }

        queue_size = self._queue.qsize()
        queue_capacity = self._queue.maxsize
        queue_usage = queue_size / queue_capacity * 100 if queue_capacity else 0
        last_db_success = self._last_db_success_at
        db_age = (
            (now - last_db_success).total_seconds() if last_db_success else None
        )
        elapsed = (now - self._started_at).total_seconds()
        persistence_stalled = self._received_ticks > 0 and (
            (db_age is None and elapsed > self.PERSISTENCE_STALE_AFTER_SECONDS)
            or (db_age is not None and db_age > self.PERSISTENCE_STALE_AFTER_SECONDS)
        )

        if not self._connected:
            status = "unhealthy"
        elif queue_usage >= 90:
            status = "unhealthy"
        elif persistence_stalled:
            status = "unhealthy"
        elif stale_assets:
            status = "degraded"
        elif queue_usage >= 70:
            status = "degraded"
        else:
            status = "healthy"

        return {
            "status": status,
            "connected": self._connected,
            "connected_at": self._connected_at.isoformat() if self._connected_at else None,
            "queue": {
                "size": queue_size,
                "capacity": queue_capacity,
                "usage_percent": round(queue_usage, 2),
            },
            "metrics": {
                "received_ticks": self._received_ticks,
                "recovered_candles": self._recovered_candles,
                "write_batches": self._write_batches,
                "write_items": self._write_items,
                "database_errors": self._db_errors,
                "connection_errors": self._connection_errors,
                "gap_events": self._gap_events,
            },
            "persistence": {
                "last_success_at": (
                    last_db_success.isoformat() if last_db_success else None
                ),
                "seconds_since_last_success": (
                    round(db_age, 2) if db_age is not None else None
                ),
                "stalled": persistence_stalled,
            },
            "assets": assets_status,
            "stale_assets": stale_assets,
            "queue_usage_percent": round(queue_usage, 2),
            "last_error": self._last_error,
        }


market_data_service = DerivMarketData()
