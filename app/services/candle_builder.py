
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal


@dataclass
class Candle:
    asset_symbol: str
    candle_start: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

    def update(self, price: Decimal) -> None:
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price


@dataclass
class _AssetState:
    candle: Candle
    last_epoch: int
    ready: bool = False


class CandleBuilder:
    """
    Builds one-minute OHLC candles from live ticks.

    The first observed minute for each asset is considered incomplete,
    because the subscription may have started in the middle of that minute.

    Ticks older than the last processed tick are ignored.

    After a WebSocket disconnection, reset() must be called so that
    an incomplete candle is not emitted after reconnection.
    """

    GRANULARITY_SECONDS = 60

    def __init__(self):
        self._states: dict[str, _AssetState] = {}

    @staticmethod
    def _minute_start(epoch: int) -> datetime:
        minute_epoch = (
            epoch - epoch % CandleBuilder.GRANULARITY_SECONDS
        )
        return datetime.fromtimestamp(
            minute_epoch,
            tz=timezone.utc,
        )

    def update(
        self,
        asset_symbol: str,
        epoch: int,
        price: Decimal,
    ) -> Candle | None:
        if not asset_symbol:
            raise ValueError("Asset symbol cannot be empty.")

        if not isinstance(epoch, int) or isinstance(epoch, bool):
            raise ValueError("Epoch must be an integer.")

        if not isinstance(price, Decimal):
            price = Decimal(str(price))

        if not price.is_finite():
            raise ValueError("Price must be finite.")

        if price <= 0:
            raise ValueError("Price must be positive.")

        candle_start = self._minute_start(epoch)
        state = self._states.get(asset_symbol)

        if state is None:
            self._states[asset_symbol] = _AssetState(
                candle=Candle(
                    asset_symbol=asset_symbol,
                    candle_start=candle_start,
                    open=price,
                    high=price,
                    low=price,
                    close=price,
                ),
                last_epoch=epoch,
            )
            return None

        # Ignore duplicated or out-of-order ticks.
        if epoch <= state.last_epoch:
            return None

        current = state.candle

        if candle_start < current.candle_start:
            return None

        if candle_start == current.candle_start:
            current.update(price)
            state.last_epoch = epoch
            return None

        # A new minute has started.
        completed = current if state.ready else None

        state.candle = Candle(
            asset_symbol=asset_symbol,
            candle_start=candle_start,
            open=price,
            high=price,
            low=price,
            close=price,
        )

        state.last_epoch = epoch
        state.ready = True

        return completed

    def current(self, asset_symbol: str) -> Candle | None:
        state = self._states.get(asset_symbol)
        return state.candle if state else None

    def current_all(self) -> dict[str, Candle]:
        return {
            symbol: state.candle
            for symbol, state in self._states.items()
        }

    def reset(self, asset_symbol: str | None = None) -> None:
        """
        Discards in-memory candle state.

        Call this after a WebSocket disconnection. Historical recovery
        must reconcile the candles lost during the interruption.
        """
        if asset_symbol is None:
            self._states.clear()
        else:
            self._states.pop(asset_symbol, None)
