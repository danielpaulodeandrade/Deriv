
from alembic import op

revision = "004_create_price_candles"
down_revision = "003_deduplicate_ticks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE price_candles (
            asset_symbol VARCHAR(32) NOT NULL
                REFERENCES assets(symbol),

            candle_start TIMESTAMPTZ NOT NULL,

            open NUMERIC(30, 12) NOT NULL,
            high NUMERIC(30, 12) NOT NULL,
            low NUMERIC(30, 12) NOT NULL,
            close NUMERIC(30, 12) NOT NULL,

            received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

            PRIMARY KEY (candle_start, asset_symbol),

            CHECK (high >= low),
            CHECK (high >= open AND high >= close),
            CHECK (low <= open AND low <= close)
        )
    """)

    op.execute("""
        SELECT create_hypertable(
            'price_candles',
            'candle_start',
            if_not_exists => TRUE
        )
    """)

    op.execute("""
        CREATE INDEX ix_price_candles_asset_time
        ON price_candles (asset_symbol, candle_start DESC)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS price_candles")
