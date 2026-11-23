import asyncio
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.db.connection import init_db_pool, close_db_pool
from app.services.deriv_market_data import DerivMarketData


@pytest.mark.asyncio
async def test_database_writer_persists_duplicate_candles_once():
    pool = await init_db_pool()
    assert pool is not None, "Não foi possível conectar ao PostgreSQL."

    candle_start = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

    candle = (
        "live",
        "R_100",
        candle_start,
        Decimal("98765.1000"),
        Decimal("98765.9000"),
        Decimal("98764.5000"),
        Decimal("98765.4321"),
    )

    service = DerivMarketData.__new__(DerivMarketData)
    service._stop = asyncio.Event()
    service._stop.set()
    service._queue = asyncio.Queue()
    service._write_batches = 0
    service._write_items = 0
    service._db_errors = 0
    service._last_db_success_at = None
    service._last_error = None

    try:
        await service._queue.put(candle)
        await service._queue.put(candle)

        await asyncio.wait_for(
            service._database_writer(),
            timeout=10,
        )

        async with pool.acquire() as conn:
            count = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM price_candles
                WHERE asset_symbol = $1
                  AND candle_start = $2
                """,
                "R_100",
                candle_start,
            )

        assert count == 1
        assert service._write_items == 2
        assert service._db_errors == 0
        assert service._queue.empty()

    finally:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM price_candles
                WHERE asset_symbol = $1
                  AND candle_start = $2
                """,
                "R_100",
                candle_start,
            )

        await close_db_pool()


@pytest.mark.asyncio
async def test_database_writer_updates_historical_candle():
    pool = await init_db_pool()
    assert pool is not None, "Não foi possível conectar ao PostgreSQL."

    candle_start = datetime(2026, 1, 1, 13, 0, tzinfo=timezone.utc)

    service = DerivMarketData.__new__(DerivMarketData)
    service._stop = asyncio.Event()
    service._stop.set()
    service._queue = asyncio.Queue()
    service._write_batches = 0
    service._write_items = 0
    service._db_errors = 0
    service._last_db_success_at = None
    service._last_error = None

    original = (
        "history", "R_100", candle_start,
        Decimal("100"), Decimal("110"),
        Decimal("90"), Decimal("105"),
    )

    updated = (
        "history", "R_100", candle_start,
        Decimal("102"), Decimal("115"),
        Decimal("95"), Decimal("112"),
    )

    try:
        await service._queue.put(original)
        await service._database_writer()

        service._stop = asyncio.Event()
        service._stop.set()

        await service._queue.put(updated)
        await service._database_writer()

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT open, high, low, close
                FROM price_candles
                WHERE asset_symbol = $1
                  AND candle_start = $2
                """,
                "R_100",
                candle_start,
            )

        assert row is not None
        assert row["open"] == Decimal("102")
        assert row["high"] == Decimal("115")
        assert row["low"] == Decimal("95")
        assert row["close"] == Decimal("112")
        assert service._write_items == 2
        assert service._db_errors == 0

    finally:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM price_candles
                WHERE asset_symbol = $1
                  AND candle_start = $2
                """,
                "R_100",
                candle_start,
            )

        await close_db_pool()
