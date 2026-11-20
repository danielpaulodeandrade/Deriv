
from datetime import datetime, timezone
from decimal import Decimal

from app.services.candle_builder import CandleBuilder


def epoch(value: str) -> int:
    return int(
        datetime.fromisoformat(value)
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )


def test_builds_correct_ohlc():
    builder = CandleBuilder()

    # Primeiro minuto: incompleto, portanto não será emitido.
    assert builder.update("R_100", epoch("2026-11-13T10:00:05"), Decimal("100")) is None
    assert builder.update("R_100", epoch("2026-11-13T10:00:15"), Decimal("105")) is None

    # Primeiro fechamento observado: descarta o minuto inicial.
    assert builder.update("R_100", epoch("2026-11-13T10:01:00"), Decimal("103")) is None

    # Segundo minuto: agora temos cobertura completa.
    assert builder.update("R_100", epoch("2026-11-13T10:01:10"), Decimal("108")) is None
    assert builder.update("R_100", epoch("2026-11-13T10:01:30"), Decimal("101")) is None
    assert builder.update("R_100", epoch("2026-11-13T10:01:50"), Decimal("106")) is None

    # Novo minuto fecha o candle anterior.
    completed = builder.update(
        "R_100",
        epoch("2026-11-13T10:02:00"),
        Decimal("110"),
    )

    assert completed is not None
    assert completed.asset_symbol == "R_100"
    assert completed.candle_start == datetime(
        2026, 11, 13, 10, 1, tzinfo=timezone.utc
    )
    assert completed.open == Decimal("103")
    assert completed.high == Decimal("108")
    assert completed.low == Decimal("101")
    assert completed.close == Decimal("106")


def test_assets_are_independent():
    builder = CandleBuilder()

    builder.update("R_100", epoch("2026-11-13T10:00:05"), Decimal("100"))
    builder.update("1HZ100V", epoch("2026-11-13T10:00:05"), Decimal("200"))

    builder.update("R_100", epoch("2026-11-13T10:01:00"), Decimal("105"))
    builder.update("1HZ100V", epoch("2026-11-13T10:01:00"), Decimal("205"))

    r100 = builder.current("R_100")
    hz100 = builder.current("1HZ100V")

    assert r100.close == Decimal("105")
    assert hz100.close == Decimal("205")


def test_ignores_out_of_order_ticks():
    builder = CandleBuilder()

    builder.update("R_100", epoch("2026-11-13T10:00:05"), Decimal("100"))
    builder.update("R_100", epoch("2026-11-13T10:01:00"), Decimal("105"))

    # Tick atrasado não pode alterar o candle atual.
    builder.update("R_100", epoch("2026-11-13T10:00:30"), Decimal("999"))

    current = builder.current("R_100")

    assert current.open == Decimal("105")
    assert current.high == Decimal("105")
    assert current.low == Decimal("105")
    assert current.close == Decimal("105")


def test_does_not_create_empty_candles():
    builder = CandleBuilder()

    builder.update("R_100", epoch("2026-11-13T10:00:05"), Decimal("100"))
    builder.update("R_100", epoch("2026-11-13T10:01:00"), Decimal("105"))

    # Salto de vários minutos sem ticks.
    completed = builder.update(
        "R_100",
        epoch("2026-11-13T10:05:00"),
        Decimal("110"),
    )

    # O candle real das 10:01 deve ser fechado.
    assert completed is not None
    assert completed.candle_start == datetime(
        2026, 11, 13, 10, 1, tzinfo=timezone.utc
    )

    # O candle atual começa às 10:05.
    current = builder.current("R_100")
    assert current.candle_start == datetime(
        2026, 11, 13, 10, 5, tzinfo=timezone.utc
    )

    # Não existem candles artificiais para 10:02, 10:03 ou 10:04.


def test_ignores_older_tick_within_same_minute():
    builder = CandleBuilder()

    builder.update("R_100", epoch("2026-11-13T09:59:59"), Decimal("90"))
    builder.update("R_100", epoch("2026-11-13T10:00:01"), Decimal("100"))
    builder.update("R_100", epoch("2026-11-13T10:00:20"), Decimal("110"))

    # Tick atrasado: não pode sobrescrever o close.
    builder.update("R_100", epoch("2026-11-13T10:00:10"), Decimal("105"))

    completed = builder.update(
        "R_100",
        epoch("2026-11-13T10:01:00"),
        Decimal("108"),
    )

    assert completed is not None
    assert completed.close == Decimal("110")


def test_reset_discards_incomplete_candle():
    builder = CandleBuilder()

    builder.update("R_100", epoch("2026-11-13T10:00:05"), Decimal("100"))

    builder.reset("R_100")

    assert builder.current("R_100") is None

    # Primeiro minuto após reset: considerado incompleto.
    builder.update("R_100", epoch("2026-11-13T10:01:05"), Decimal("105"))

    completed = builder.update(
        "R_100",
        epoch("2026-11-13T10:02:00"),
        Decimal("110"),
    )

    assert completed is None
