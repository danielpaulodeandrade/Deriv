
from alembic import op

revision = "003_deduplicate_ticks"
down_revision = "002_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE UNIQUE INDEX uq_price_ticks_asset_time_price
        ON price_ticks (asset_symbol, occurred_at, price)
    """)


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS uq_price_ticks_asset_time_price
    """)
