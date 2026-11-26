import asyncio
import json
import logging
from contextlib import suppress
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

from websockets.asyncio.client import connect

from app.core.config import settings
from app.db.connection import get_db_pool

logger = logging.getLogger(__name__)

class InvalidHistoricalCandleError(ValueError):
    """Raised when Deriv returns invalid historical candle data."""

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
        self._current_candles = {}
        self._connection = None
        self._consumer_task = None
        self._writer_task = None
        self._recovery_task = None
        self._recovery_requested = asyncio.Event()
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

            tasks = (
                self._writer_task,
                self._consumer_task,
                self._recovery_task,
            )

            running = [
                task is not None and not task.done()
                for task in tasks
            ]

            if all(running):
                logger.warning("Deriv market data service is already running.")
                return

            if any(running):
                raise RuntimeError(
                    "Deriv market data service is in a partial state. "
                    "Call stop() before starting it again."
                )

            self._stop.clear()
            self._recovery_requested.set()
            self._started_at = datetime.now(timezone.utc)

            try:
                self._writer_task = asyncio.create_task(
                    self._database_writer(),
                    name="deriv-candle-writer",
                )

                self._consumer_task = asyncio.create_task(
                    self._consume_ticks(),
                    name="deriv-ohlc-consumer",
                )

                self._recovery_task = asyncio.create_task(
                    self._history_recovery_worker(),
                    name="deriv-candle-recovery",
                )

            except Exception:
                self._stop.set()

                for task in (
                    self._consumer_task,
                    self._recovery_task,
                ):
                    if task is not None and not task.done():
                        task.cancel()

                await asyncio.gather(
                    *(
                        task for task in (
                            self._writer_task,
                            self._consumer_task,
                            self._recovery_task,
                        )
                        if task is not None
                    ),
                    return_exceptions=True,
                )

                self._writer_task = None
                self._consumer_task = None
                self._recovery_task = None
                raise

            logger.info(
                "Deriv market data service started: %s",
                self.symbols,
            )

    async def _history_recovery_worker(self):
        while not self._stop.is_set():
            await self._recovery_requested.wait()

            if self._stop.is_set():
                break

            self._recovery_requested.clear()

            try:
                # Aguarda a persistência dos candles recebidos ao vivo.
                await self._queue.join()

                if self._stop.is_set():
                    break

                await self._recover_missing_candles()

            except asyncio.CancelledError:
                raise

            except InvalidHistoricalCandleError:
                # O erro já foi registrado na recuperação do ativo.
                # Aguarda uma nova solicitação de recuperação.
                continue

            except Exception:
                self._last_error = "Unexpected history recovery worker failure"
                logger.exception(
                    "Unexpected history recovery worker failure. "
                    "Retrying in 5 seconds."
                )

                try:
                    await asyncio.wait_for(
                        self._stop.wait(),
                        timeout=5,
                    )
                except asyncio.TimeoutError:
                    self._recovery_requested.set()

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

                try:
                    if writer_task is not None:
                        pending = self._queue.qsize()

                        if pending:
                            logger.info(
                                "Service shutdown waiting for candle persistence. "
                                "%d candles remain queued.",
                                pending,
                            )

                        await writer_task
                finally:
                    self._connection = None
                    self._connected = False
                    self._consumer_task = None
                    self._writer_task = None
                    self._recovery_task = None
                    self._current_candles.clear()

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
        has_connected = False

        try:
            while not self._stop.is_set():
                try:
                    logger.info("Connecting to Deriv live OHLC WebSocket.")

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
                        self._current_candles.clear()

                        logger.info("Connected to Deriv live OHLC WebSocket.")

                        for req_id, symbol in enumerate(self.symbols, start=1):
                            if self._stop.is_set():
                                break

                            await ws.send(
                                json.dumps({
                                    "ticks_history": symbol,
                                    "style": "candles",
                                    "granularity": self.GRANULARITY_SECONDS,
                                    "subscribe": 1,
                                    "req_id": req_id,
                                })
                            )

                            logger.info(
                                "Subscribed to OHLC candles: %s",
                                symbol,
                            )

                        if has_connected:
                            self._recovery_requested.set()

                        has_connected = True

                        async for raw_message in ws:
                            if self._stop.is_set():
                                break

                            await self._process_message(raw_message)

                        self._connection = None
                        self._connected = False
                        self._current_candles.clear()

                        if not self._stop.is_set():
                            raise ConnectionError(
                                "Deriv live OHLC WebSocket disconnected."
                            )

                except asyncio.CancelledError:
                    raise

                except Exception:
                    self._connection = None
                    self._connected = False
                    self._current_candles.clear()

                    if self._stop.is_set():
                        break

                    self._connection_errors += 1
                    self._last_error = "Live OHLC WebSocket failure"

                    logger.exception(
                        "Deriv live connection failed. "
                        "Reconnecting in %.1f seconds.",
                        delay,
                    )

                    try:
                        await asyncio.wait_for(
                            self._stop.wait(),
                            timeout=delay,
                        )
                    except asyncio.TimeoutError:
                        pass

                    delay = min(delay * 2, 60)

        finally:
            self._connection = None
            self._connected = False
            self._current_candles.clear()

    async def _process_message(self, raw_message: str):
        try:
            message = json.loads(raw_message)

            if "error" in message:
                logger.error("Deriv API error: %s", message["error"])
                return

            if message.get("msg_type") != "ohlc":
                return

            ohlc = message.get("ohlc") or {}
            symbol = ohlc.get("symbol")

            if symbol not in self.symbols:
                logger.warning("Unexpected symbol received: %s", symbol)
                return

            open_time = int(ohlc["open_time"])
            epoch = int(ohlc["epoch"])

            prices = {
                key: Decimal(str(ohlc[key]))
                for key in ("open", "high", "low", "close")
            }

            values = tuple(prices.values())

            if any(not value.is_finite() or value <= 0 for value in values):
                raise ValueError("Invalid OHLC prices.")

            if (
                prices["high"] < max(prices["open"], prices["close"], prices["low"])
                or prices["low"] > min(prices["open"], prices["close"], prices["high"])
            ):
                raise ValueError("Inconsistent OHLC prices.")

            current = self._current_candles.get(symbol)

            if current is not None:
                previous_open_time = current["open_time"]

                if open_time < previous_open_time:
                    return

                if open_time == previous_open_time:
                    current.update(prices)
                else:
                    await self._queue.put((
                        "live",
                        symbol,
                        datetime.fromtimestamp(previous_open_time, tz=timezone.utc),
                        current["open"],
                        current["high"],
                        current["low"],
                        current["close"],
                    ))

                    if open_time - previous_open_time > self.GRANULARITY_SECONDS:
                        self._gap_events += 1

                    self._current_candles[symbol] = {
                        "open_time": open_time,
                        **prices,
                    }
            else:
                self._current_candles[symbol] = {
                    "open_time": open_time,
                    **prices,
                }

            previous_epoch = self._last_tick_epoch.get(symbol)

            if previous_epoch is not None and epoch - previous_epoch > 5:
                self._gap_events += 1

            self._last_tick_epoch[symbol] = max(epoch, previous_epoch or epoch)
            self._last_tick_received_at[symbol] = datetime.now(timezone.utc)
            self._received_ticks += 1

        except (ValueError, TypeError, KeyError, InvalidOperation, OverflowError):
            logger.exception("Invalid OHLC message received.")

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

            response_req_id = message.get("req_id")

            # Ignora respostas identificadas como pertencentes a outra solicitação.
            if (
                response_req_id is not None
                and response_req_id != self.HISTORY_REQUEST_ID
            ):
                continue

            # Erros sem req_id ou com o req_id esperado devem ser tratados.
            if "error" in message:
                raise RuntimeError(
                    f"Candle history error for {symbol}: {message['error']}"
                )

            # Só aceita candles vinculados à solicitação atual.
            if response_req_id != self.HISTORY_REQUEST_ID:
                continue

            if message.get("msg_type") != "candles":
                continue

            return message.get("candles") or []

        return []

    async def _recover_missing_candles(
        self, cursors: dict[str, int | None] | None = None
    ):
        delay = settings.DERIV_RECONNECT_DELAY_SECONDS
        symbol_index = 0

        while not self._stop.is_set() and symbol_index < len(self.symbols):
            try:
                async with connect(
                    settings.DERIV_WS_URL,
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=5,
                ) as ws:
                    while (
                        not self._stop.is_set()
                        and symbol_index < len(self.symbols)
                    ):
                        symbol = self.symbols[symbol_index]

                        try:
                            if cursors is None:
                                last_epoch = (
                                    await self._last_persisted_candle_epoch(symbol)
                                )
                            else:
                                last_epoch = cursors.get(symbol)

                            if last_epoch is None:
                                start = int(
                                    (
                                        datetime.now(timezone.utc)
                                        - timedelta(days=self.HISTORY_DAYS)
                                    ).timestamp()
                                )
                                logger.info(
                                    "Initial candle history for %s: last %d days.",
                                    symbol,
                                    self.HISTORY_DAYS,
                                )
                            else:
                                start = max(
                                    0,
                                    int(last_epoch) - self.GRANULARITY_SECONDS,
                                )
                                logger.info(
                                    "Recovering candles for %s from epoch %d.",
                                    symbol,
                                    start,
                                )

                            end = "latest"
                            recovered = 0

                            while not self._stop.is_set():
                                candles = await self._request_history(
                                    ws, symbol, start, end
                                )

                                if not candles:
                                    break

                                try:
                                    epochs = []

                                    for item in candles:
                                        epoch = item["epoch"]

                                        if isinstance(epoch, bool) or not isinstance(epoch, int):
                                            raise ValueError(f"Invalid epoch type: {epoch!r}")

                                        if epoch <= 0:
                                            raise ValueError(f"Invalid epoch value: {epoch}")

                                        if epoch % self.GRANULARITY_SECONDS != 0:
                                            raise ValueError(f"Epoch is not aligned to 60 seconds: {epoch}")

                                        epochs.append(epoch)

                                except (KeyError, TypeError, ValueError) as exc:
                                    raise InvalidHistoricalCandleError(
                                        f"Invalid candle epoch returned for {symbol}: {candles}"
                                    ) from exc

                                earliest = min(epochs)

                                current_minute = (
                                    int(datetime.now(timezone.utc).timestamp())
                                    // self.GRANULARITY_SECONDS
                                    * self.GRANULARITY_SECONDS
                                )

                                for item, epoch in zip(candles, epochs):
                                    candle_epoch = (
                                        epoch - epoch % self.GRANULARITY_SECONDS
                                    )

                                    if (
                                        candle_epoch < start
                                        or candle_epoch >= current_minute
                                    ):
                                        continue

                                    try:
                                        open_price = Decimal(str(item["open"]))
                                        high_price = Decimal(str(item["high"]))
                                        low_price = Decimal(str(item["low"]))
                                        close_price = Decimal(str(item["close"]))
                                    except (
                                        KeyError,
                                        InvalidOperation,
                                        TypeError,
                                        ValueError,
                                    ) as exc:
                                        raise InvalidHistoricalCandleError(
                                            f"Invalid candle returned for "
                                            f"{symbol}: {item}"
                                        ) from exc

                                    values = (
                                        open_price,
                                        high_price,
                                        low_price,
                                        close_price,
                                    )

                                    if any(
                                        not value.is_finite() or value <= 0
                                        for value in values
                                    ):
                                        raise InvalidHistoricalCandleError(
                                            f"Invalid OHLC values returned for "
                                            f"{symbol}: {item}"
                                        )

                                    if (
                                        high_price
                                        < max(open_price, close_price, low_price)
                                        or low_price
                                        > min(open_price, close_price, high_price)
                                    ):
                                        raise InvalidHistoricalCandleError(
                                            f"Inconsistent OHLC values returned "
                                            f"for {symbol}: {item}"
                                        )

                                    try:
                                        candle_start = datetime.fromtimestamp(
                                            candle_epoch,
                                            tz=timezone.utc,
                                        )
                                    except (OverflowError, OSError, ValueError) as exc:
                                        raise InvalidHistoricalCandleError(
                                            f"Invalid candle timestamp returned for "
                                            f"{symbol}: {candle_epoch}"
                                        ) from exc

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

                                if (
                                    earliest <= start
                                    or len(candles) < self.HISTORY_PAGE_SIZE
                                ):
                                    break

                                next_end = earliest - 1

                                if (
                                    isinstance(end, int)
                                    and next_end >= end
                                ):
                                    raise RuntimeError(
                                        f"Candle history pagination made no progress for {symbol}."
                                    )

                                end = next_end

                            if self._stop.is_set():
                                break

                            logger.info(
                                "Candle history recovery completed for %s: "
                                "%d candles queued.",
                                symbol,
                                recovered,
                            )

                            # Só avança depois de concluir o ativo.
                            symbol_index += 1

                            # Um ativo concluído reinicia o backoff.
                            delay = settings.DERIV_RECONNECT_DELAY_SECONDS

                        except InvalidHistoricalCandleError:
                            self._last_error = (
                                f"Invalid historical candle data for {symbol}"
                            )
                            logger.exception(
                                "Historical recovery stopped for %s: "
                                "invalid candle data.",
                                symbol,
                            )
                            raise

                        except Exception:
                            self._last_error = (
                                f"Candle history recovery failure for {symbol}"
                            )
                            logger.exception(
                                "Candle history recovery failed for %s. "
                                "Reconnecting and retrying this asset.",
                                symbol,
                            )
                            break

            except asyncio.CancelledError:
                raise

            except InvalidHistoricalCandleError:
                raise

            except Exception:
                symbol = (
                    self.symbols[symbol_index]
                    if symbol_index < len(self.symbols)
                    else "unknown"
                )
                self._last_error = (
                    f"Candle history connection failure for {symbol}"
                )
                logger.exception(
                    "Candle history connection failed for %s. "
                    "Retrying in %.1f seconds.",
                    symbol,
                    delay,
                )

            if self._stop.is_set() or symbol_index >= len(self.symbols):
                break

            try:
                await asyncio.wait_for(
                    self._stop.wait(),
                    timeout=delay,
                )
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
                    if self._stop.is_set():
                        logger.warning(
                            "Service shutdown waiting for database availability. "
                            "%d candles remain in the current batch.",
                            len(batch),
                        )
                    else:
                        logger.error(
                            "Database pool unavailable. Retrying candle batch."
                        )

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

                    if self._stop.is_set():
                        logger.exception(
                            "Service shutdown waiting for database recovery. "
                            "Failed to persist %d candles. Retrying.",
                            len(batch),
                        )
                    else:
                        logger.exception(
                            "Failed to persist %d candles. Retrying.",
                            len(batch),
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
