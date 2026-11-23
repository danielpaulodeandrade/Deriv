import asyncio
import json

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

import app.services.deriv_market_data as market_data_module
from app.services.deriv_market_data import DerivMarketData

from app.services.candle_builder import CandleBuilder

class FakeWebSocket:
    def __init__(self, response):
        self.response = json.dumps(response)
        self.sent_messages = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def send(self, message):
        self.sent_messages.append(json.loads(message))

    async def recv(self):
        return self.response


class FakeAsyncContext:
    def __init__(self, value):
        self.value = value

    async def __aenter__(self):
        return self.value

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self):
        self.executed_query = None
        self.executed_batch = None

    def transaction(self):
        return FakeAsyncContext(self)

    async def executemany(self, query, batch):
        self.executed_query = query
        self.executed_batch = list(batch)


class FakePool:
    def __init__(self, connection):
        self.connection = connection

    def acquire(self):
        return FakeAsyncContext(self.connection)

def create_service():
    service = DerivMarketData.__new__(DerivMarketData)

    service.symbols = ["R_100"]
    service._stop = asyncio.Event()
    service._queue = asyncio.Queue(maxsize=100)

    service._recovered_candles = 0

    service._write_batches = 0
    service._write_items = 0
    service._db_errors = 0
    service._last_db_success_at = None
    service._last_error = None

    return service

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_recovery_queues_candles_from_persisted_cursor(
    monkeypatch,
):
    service = create_service()
    service._last_persisted_candle_epoch = AsyncMock(return_value=120)

    response = {
        "req_id": DerivMarketData.HISTORY_REQUEST_ID,
        "msg_type": "candles",
        "candles": [
            {
                "epoch": 60,
                "open": "1.10",
                "high": "1.20",
                "low": "1.05",
                "close": "1.15",
            },
            {
                "epoch": 120,
                "open": "1.15",
                "high": "1.30",
                "low": "1.10",
                "close": "1.25",
            },
        ],
    }

    fake_ws = FakeWebSocket(response)

    monkeypatch.setattr(
        market_data_module,
        "connect",
        lambda *args, **kwargs: fake_ws,
    )

    await service._recover_missing_candles(
        {"R_100": 120}
    )

    assert service._recovered_candles == 2
    assert service._queue.qsize() == 2

    first = service._queue.get_nowait()
    second = service._queue.get_nowait()

    assert first[0] == "history"
    assert first[1] == "R_100"
    assert int(first[2].timestamp()) == 60
    assert first[3:] == (
        Decimal("1.10"),
        Decimal("1.20"),
        Decimal("1.05"),
        Decimal("1.15"),
    )

    assert second[0] == "history"
    assert second[1] == "R_100"
    assert int(second[2].timestamp()) == 120
    assert second[3:] == (
        Decimal("1.15"),
        Decimal("1.30"),
        Decimal("1.10"),
        Decimal("1.25"),
    )

    request = fake_ws.sent_messages[0]

    assert request["ticks_history"] == "R_100"
    assert request["start"] == 60
    assert request["end"] == "latest"
    assert request["style"] == "candles"
    assert request["granularity"] == 60


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_database_writer_uses_conflict_protection(
    monkeypatch,
):
    service = create_service()

    candle_start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    candle = (
        "live",
        "R_100",
        candle_start,
        Decimal("1.10"),
        Decimal("1.30"),
        Decimal("1.05"),
        Decimal("1.20"),
    )

    await service._queue.put(candle)
    await service._queue.put(candle)

    service._stop.set()

    fake_connection = FakeConnection()
    fake_pool = FakePool(fake_connection)

    monkeypatch.setattr(
        market_data_module,
        "get_db_pool",
        lambda: fake_pool,
    )

    await service._database_writer()

    assert fake_connection.executed_batch is not None
    assert len(fake_connection.executed_batch) == 2

    query = fake_connection.executed_query.upper()

    assert "INSERT INTO PRICE_CANDLES" in query
    assert "ON CONFLICT" in query
    assert "DO NOTHING" in query

    assert service._write_batches == 1
    assert service._write_items == 2
    assert service._db_errors == 0
    assert service._queue.empty()
    assert service._last_db_success_at is not None


class FakeReconnectWebSocket:
    def __init__(self, service, stop_after_connect=False):
        self.service = service
        self.stop_after_connect = stop_after_connect
        self.sent = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def send(self, message):
        self.sent.append(message)

    async def messages(self):
        if self.stop_after_connect:
            await asyncio.sleep(0)
            self.service._stop.set()

        if False:
            yield ""

    def __aiter__(self):
        return self.messages()


class FakeReconnectContext:
    def __init__(self, websocket):
        self.websocket = websocket

    async def __aenter__(self):
        return self.websocket

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_reconnect_restarts_connection_and_history_recovery(
    monkeypatch,
):
    service = DerivMarketData.__new__(DerivMarketData)

    service.symbols = ["R_100"]
    service._stop = asyncio.Event()
    service._connection = None
    service._recovery_task = None
    service._connected = False
    service._connected_at = None
    service._connection_errors = 0
    service._last_error = None
    service._candle_builder = CandleBuilder()

    # Simula o Ãºltimo tick persistido no banco.
    service._last_persisted_candle_epoch = AsyncMock(return_value=100)

    monkeypatch.setattr(
        market_data_module.settings,
        "DERIV_RECONNECT_DELAY_SECONDS",
        0.01,
    )

    connections = []
    recovery_calls = 0

    async def fake_recovery(cursors=None):
        nonlocal recovery_calls
        recovery_calls += 1

        assert cursors == {"R_100": 100}

    service._recover_missing_candles = fake_recovery

    def fake_connect(*args, **kwargs):
        stop_after_connect = len(connections) == 1

        websocket = FakeReconnectWebSocket(
            service,
            stop_after_connect=stop_after_connect,
        )

        connections.append(websocket)
        return FakeReconnectContext(websocket)

    monkeypatch.setattr(
        market_data_module,
        "connect",
        fake_connect,
    )

    await asyncio.wait_for(
        service._consume_ticks(),
        timeout=5,
    )

    if service._recovery_task is not None:
        await asyncio.wait_for(
            service._recovery_task,
            timeout=5,
        )

    assert len(connections) == 2
    assert recovery_calls == 2
    assert service._last_persisted_candle_epoch.await_count == 2
    assert service._connection_errors == 1
    assert service._connected is False
    assert service._stop.is_set()


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_recovery_retries_after_websocket_failure(monkeypatch):
    service = create_service()
    service._last_error = None
    service._last_persisted_candle_epoch = AsyncMock(return_value=120)

    monkeypatch.setattr(
        market_data_module.settings,
        "DERIV_RECONNECT_DELAY_SECONDS",
        0.01,
    )

    attempts = 0

    class FakeWS:
        async def send(self, message):
            pass

        async def recv(self):
            nonlocal attempts
            attempts += 1

            if attempts == 1:
                raise ConnectionError("Simulated WebSocket failure")

            return json.dumps({
                "msg_type": "candles",
                "req_id": service.HISTORY_REQUEST_ID,
                "candles": [
                    {
                        "epoch": 60,
                        "open": "1.10",
                        "high": "1.20",
                        "low": "1.05",
                        "close": "1.15",
                    },
                    {
                        "epoch": 120,
                        "open": "1.15",
                        "high": "1.30",
                        "low": "1.10",
                        "close": "1.25",
                    },
                ],
            })

    class FakeContext:
        async def __aenter__(self):
            return FakeWS()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(
        market_data_module,
        "connect",
        lambda *args, **kwargs: FakeContext(),
    )

    await service._recover_missing_candles()

    assert attempts == 2
    assert service._last_persisted_candle_epoch.await_count == 2
    assert service._queue.qsize() == 2
    assert service._recovered_candles == 2


@pytest.mark.asyncio
async def test_database_writer_retries_failed_batch_without_losing_ticks(
    monkeypatch,
):
    service = DerivMarketData.__new__(DerivMarketData)

    service._stop = asyncio.Event()
    service._stop.set()

    service._queue = asyncio.Queue()
    service._write_batches = 0
    service._write_items = 0
    service._db_errors = 0
    service._last_db_success_at = None
    service._last_error = None

    candle = (
        "live",
        "R_100",
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        Decimal("1.20"),
        Decimal("1.30"),
        Decimal("1.10"),
        Decimal("1.25"),
    )

    await service._queue.put(candle)
    await service._queue.put(candle)

    class FakeTransaction:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeConnection:
        def __init__(self):
            self.attempts = 0
            self.batches = []

        def transaction(self):
            return FakeTransaction()

        async def executemany(self, query, batch):
            self.attempts += 1
            self.batches.append(list(batch))

            if self.attempts == 1:
                raise RuntimeError("Simulated database failure")

    class FakeAcquire:
        def __init__(self, connection):
            self.connection = connection

        async def __aenter__(self):
            return self.connection

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakePool:
        def __init__(self, connection):
            self.connection = connection

        def acquire(self):
            return FakeAcquire(self.connection)

    connection = FakeConnection()
    pool = FakePool(connection)

    monkeypatch.setattr(
        market_data_module,
        "get_db_pool",
        lambda: pool,
    )

    monkeypatch.setattr(
        market_data_module.asyncio,
        "sleep",
        AsyncMock(return_value=None),
    )

    await service._database_writer()

    assert connection.attempts == 2
    assert connection.batches[0] == connection.batches[1]
    assert len(connection.batches[1]) == 2

    assert service._queue.empty()
    assert service._queue._unfinished_tasks == 0

    assert service._db_errors == 1
    assert service._write_batches == 1
    assert service._write_items == 2
    assert service._last_db_success_at is not None


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_live_and_recovery_candles_are_both_preserved():
    service = DerivMarketData.__new__(DerivMarketData)

    service.symbols = ["R_100"]
    service._queue = asyncio.Queue()
    service._candle_builder = CandleBuilder()
    service._recovered_candles = 0
    service._received_ticks = 0
    service._last_tick_epoch = {}
    service._last_tick_received_at = {}
    service._gap_events = 0

    # Prepara o builder para que o candle do minuto 120 seja fechado.
    service._candle_builder.update(
        "R_100", 60, Decimal("1.10")
    )
    service._candle_builder.update(
        "R_100", 120, Decimal("1.20")
    )

    # Candle histórico recuperado.
    historical_candle = (
        "history",
        "R_100",
        datetime.fromtimestamp(60, tz=timezone.utc),
        Decimal("1.10"),
        Decimal("1.20"),
        Decimal("1.05"),
        Decimal("1.15"),
    )

    await service._queue.put(historical_candle)
    service._recovered_candles += 1

    # O tick no epoch 180 fecha o candle iniciado no epoch 120.
    live_message = json.dumps({
        "msg_type": "tick",
        "tick": {
            "symbol": "R_100",
            "epoch": 180,
            "quote": "1.30",
        },
    })

    await service._process_message(live_message)

    queued_candles = []

    while not service._queue.empty():
        queued_candles.append(service._queue.get_nowait())

    assert len(queued_candles) == 2

    sources = {item[0] for item in queued_candles}
    assert sources == {"history", "live"}

    live_candle = next(
        item for item in queued_candles if item[0] == "live"
    )

    assert live_candle[1] == "R_100"
    assert int(live_candle[2].timestamp()) == 120
    assert live_candle[3:] == (
        Decimal("1.20"),
        Decimal("1.20"),
        Decimal("1.20"),
        Decimal("1.20"),
    )

    assert service._recovered_candles == 1
    assert service._received_ticks == 1
    assert service._last_tick_epoch["R_100"] == 180


def create_lifecycle_service():
    service = DerivMarketData()
    service.symbols = ["R_100"]
    return service


@pytest.mark.asyncio
async def test_start_called_twice_does_not_create_duplicate_tasks():
    service = create_lifecycle_service()

    async def wait_until_stopped():
        await service._stop.wait()

    service._database_writer = wait_until_stopped
    service._consume_ticks = wait_until_stopped

    await service.start()
    first_writer = service._writer_task
    first_consumer = service._consumer_task

    await service.start()

    assert service._writer_task is first_writer
    assert service._consumer_task is first_consumer
    assert not first_writer.done()
    assert not first_consumer.done()

    await service.stop()

    assert first_writer.done()
    assert first_consumer.done()
    assert service._writer_task is None
    assert service._consumer_task is None


@pytest.mark.asyncio
async def test_stop_waits_for_writer_without_cancelling_it():
    service = create_lifecycle_service()
    writer_started = asyncio.Event()
    release_writer = asyncio.Event()

    async def fake_writer():
        writer_started.set()
        await release_writer.wait()

    async def fake_consumer():
        await service._stop.wait()

    service._database_writer = fake_writer
    service._consume_ticks = fake_consumer

    await service.start()
    await asyncio.wait_for(writer_started.wait(), timeout=1)

    stop_task = asyncio.create_task(service.stop())
    await asyncio.sleep(0)

    assert not stop_task.done()
    assert not service._writer_task.cancelled()

    release_writer.set()
    await asyncio.wait_for(stop_task, timeout=1)

    assert service._writer_task is None
    assert service._consumer_task is None


@pytest.mark.asyncio
async def test_stop_cancels_recovery_task():
    service = create_lifecycle_service()
    recovery_started = asyncio.Event()

    async def fake_writer():
        await service._stop.wait()

    async def fake_consumer():
        await service._stop.wait()

    async def fake_recovery():
        recovery_started.set()
        await asyncio.Future()

    service._database_writer = fake_writer
    service._consume_ticks = fake_consumer

    await service.start()
    recovery_task = asyncio.create_task(fake_recovery())
    service._recovery_task = recovery_task

    await asyncio.wait_for(recovery_started.wait(), timeout=1)
    await asyncio.wait_for(service.stop(), timeout=1)

    assert recovery_task.cancelled()
    assert service._recovery_task is None


@pytest.mark.asyncio
async def test_service_can_restart_after_stop():
    service = create_lifecycle_service()

    async def wait_until_stopped():
        await service._stop.wait()

    service._database_writer = wait_until_stopped
    service._consume_ticks = wait_until_stopped

    await service.start()
    first_writer = service._writer_task
    first_consumer = service._consumer_task

    await service.stop()

    assert service._stop.is_set()
    assert service._writer_task is None
    assert service._consumer_task is None

    await service.start()
    second_writer = service._writer_task
    second_consumer = service._consumer_task

    assert not service._stop.is_set()
    assert second_writer is not first_writer
    assert second_consumer is not first_consumer
    assert not second_writer.done()
    assert not second_consumer.done()

    await service.stop()

    assert service._writer_task is None
    assert service._consumer_task is None


@pytest.mark.asyncio
async def test_stop_cleans_state_when_websocket_close_fails():
    service = create_lifecycle_service()

    async def wait_until_stopped():
        await service._stop.wait()

    class FailingConnection:
        async def close(self):
            raise RuntimeError("Simulated WebSocket close failure")

    service._database_writer = wait_until_stopped
    service._consume_ticks = wait_until_stopped
    service._connection = FailingConnection()
    service._connected = True

    await asyncio.wait_for(service.start(), timeout=1)
    await asyncio.wait_for(service.stop(), timeout=1)

    assert service._stop.is_set()
    assert service._connection is None
    assert service._connected is False
    assert service._writer_task is None
    assert service._consumer_task is None
    assert service._recovery_task is None


@pytest.mark.asyncio
async def test_recovery_paginates_more_than_one_history_page(monkeypatch):
    service = create_service()
    service._queue = asyncio.Queue()
    service._last_error = None
    service._last_persisted_candle_epoch = AsyncMock(return_value=0)

    page_size = DerivMarketData.HISTORY_PAGE_SIZE
    first_epoch = 1_000_000
    second_page_epoch = first_epoch - 10 * 60

    first_page = [
        {
            "epoch": first_epoch + index * 60,
            "open": "1.10",
            "high": "1.20",
            "low": "1.05",
            "close": "1.15",
        }
        for index in range(page_size)
    ]

    second_page = [
        {
            "epoch": second_page_epoch + index * 60,
            "open": "1.10",
            "high": "1.20",
            "low": "1.05",
            "close": "1.15",
        }
        for index in range(10)
    ]

    responses = [first_page, second_page]
    requests = []

    class PaginatedWebSocket:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def send(self, message):
            requests.append(json.loads(message))

        async def recv(self):
            response = responses.pop(0)
            return json.dumps({
                "req_id": DerivMarketData.HISTORY_REQUEST_ID,
                "msg_type": "candles",
                "candles": response,
            })

    monkeypatch.setattr(
        market_data_module,
        "connect",
        lambda *args, **kwargs: PaginatedWebSocket(),
    )

    await service._recover_missing_candles({"R_100": 0})

    assert len(requests) == 2
    assert requests[0]["end"] == "latest"
    assert requests[1]["end"] == first_epoch - 1

    assert service._queue.qsize() == page_size + 10
    assert service._recovered_candles == page_size + 10
    assert responses == []

    queued_items = []

    while not service._queue.empty():
        queued_items.append(service._queue.get_nowait())

    candle_epochs = [
        int(item[2].timestamp())
        for item in queued_items
    ]

    assert len(candle_epochs) == 5010
    assert len(set(candle_epochs)) == 5010

    sorted_epochs = sorted(candle_epochs)

    assert all(
        current - previous == 60
        for previous, current in zip(
            sorted_epochs,
            sorted_epochs[1:],
        )
    )


@pytest.mark.asyncio
async def test_initial_recovery_without_persisted_cursor(monkeypatch):
    service = create_service()
    service._last_persisted_candle_epoch = AsyncMock(return_value=None)

    now_epoch = int(datetime.now(timezone.utc).timestamp())
    candle_epoch = (now_epoch // 60 - 2) * 60

    response = {
        "req_id": DerivMarketData.HISTORY_REQUEST_ID,
        "msg_type": "candles",
        "candles": [
            {
                "epoch": candle_epoch,
                "open": "1.10",
                "high": "1.20",
                "low": "1.05",
                "close": "1.15",
            },
        ],
    }


    fake_ws = FakeWebSocket(response)

    monkeypatch.setattr(
        market_data_module,
        "connect",
        lambda *args, **kwargs: fake_ws,
    )

    before = int(datetime.now(timezone.utc).timestamp())

    await service._recover_missing_candles({"R_100": None})

    after = int(datetime.now(timezone.utc).timestamp())

    request = fake_ws.sent_messages[0]

    expected_start_min = before - service.HISTORY_DAYS * 86400
    expected_start_max = after - service.HISTORY_DAYS * 86400

    assert expected_start_min <= request["start"] <= expected_start_max
    assert request["end"] == "latest"
    assert request["ticks_history"] == "R_100"
    assert request["style"] == "candles"
    assert request["granularity"] == 60

    assert service._recovered_candles == 1
    assert service._queue.qsize() == 1

    candle = service._queue.get_nowait()

    assert candle[0] == "history"
    assert candle[1] == "R_100"
    assert int(candle[2].timestamp()) == candle_epoch
