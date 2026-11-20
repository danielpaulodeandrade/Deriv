
import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from app.services.deriv_market_data import DerivMarketData


def create_service():
    """Cria uma instância isolada para testar o monitoramento."""
    service = DerivMarketData.__new__(DerivMarketData)

    now = datetime.now(timezone.utc)

    service.symbols = ["1HZ100V", "R_100"]
    service._started_at = now - timedelta(seconds=2)
    service._recovered_candles = 0

    service._connected = True
    service._connected_at = now

    service._last_tick_received_at = {
        "1HZ100V": now,
        "R_100": now,
    }

    service._last_tick_epoch = {
        "1HZ100V": 1794086481,
        "R_100": 1794086480,
    }

    service._received_ticks = 10
    service._write_batches = 10
    service._write_items = 10

    service._db_errors = 0
    service._connection_errors = 0
    service._gap_events = 0

    service._last_db_success_at = now
    service._last_error = None

    service._queue = asyncio.Queue(maxsize=100)

    return service


def test_health_is_healthy():
    service = create_service()

    result = service.get_status()

    assert result["status"] == "healthy"
    assert result["connected"] is True
    assert result["persistence"]["stalled"] is False
    assert result["stale_assets"] == []


def test_health_is_degraded_when_asset_is_stale():
    service = create_service()

    service._last_tick_received_at["1HZ100V"] = (
        datetime.now(timezone.utc)
        - timedelta(seconds=service.STALE_AFTER_SECONDS + 5)
    )

    result = service.get_status()

    assert result["status"] == "degraded"
    assert "1HZ100V" in result["stale_assets"]


def test_health_is_unhealthy_when_disconnected():
    service = create_service()
    service._connected = False

    result = service.get_status()

    assert result["status"] == "unhealthy"


def test_health_is_unhealthy_when_queue_is_90_percent_full():
    service = create_service()
    service._queue = asyncio.Queue(maxsize=10)

    for _ in range(9):
        service._queue.put_nowait("test")

    result = service.get_status()

    assert result["status"] == "unhealthy"
    assert result["queue"]["usage_percent"] == 90


def test_health_is_unhealthy_when_persistence_stalls():
    service = create_service()
    service._received_ticks = 1

    service._last_db_success_at = (
        datetime.now(timezone.utc) - timedelta(seconds=91)
    )

    result = service.get_status()

    assert result["status"] == "unhealthy"
    assert result["persistence"]["stalled"] is True


def test_recovered_candles_are_reported_separately():
    service = create_service()

    service._received_ticks = 10
    service._recovered_candles = 5

    result = service.get_status()

    assert result["metrics"]["received_ticks"] == 10
    assert result["metrics"]["recovered_candles"] == 5
    assert "recovered_ticks" not in result["metrics"]