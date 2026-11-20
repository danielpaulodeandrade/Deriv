from alembic import op

revision = "001_enable_timescaledb"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")


def downgrade() -> None:
    raise NotImplementedError(
        "Downgrade da extensão TimescaleDB não é automático."
    )