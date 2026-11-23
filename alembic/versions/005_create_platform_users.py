
from alembic import op

revision = "005_create_platform_users"
down_revision = "004_create_price_candles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Usuarios da plataforma
    op.execute("""
        CREATE TABLE platform_users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(254) NOT NULL,
            password_hash TEXT NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'customer'
                CHECK (role IN ('customer', 'admin')),
            status VARCHAR(20) NOT NULL DEFAULT 'pending'
                CHECK (status IN ('active', 'pending', 'suspended')),
            email_verified_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_platform_users_email UNIQUE (email),
            CONSTRAINT ck_platform_users_email_lowercase
                CHECK (email = LOWER(email)),
            CONSTRAINT ck_platform_users_active_verified
                CHECK (status <> 'active' OR email_verified_at IS NOT NULL)
        )
    """)

    # Contas Deriv vinculadas aos usuarios
    op.execute("""
        CREATE TABLE deriv_accounts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL
                REFERENCES platform_users(id) ON DELETE RESTRICT,
            deriv_account_id VARCHAR(32) NOT NULL,
            account_type VARCHAR(10) NOT NULL
                CHECK (account_type IN ('demo', 'real')),
            token_encrypted BYTEA NOT NULL,
            token_expires_at TIMESTAMPTZ,
            currency VARCHAR(10),
            status VARCHAR(20) NOT NULL DEFAULT 'pending'
                CHECK (status IN (
                    'active', 'pending', 'expired', 'revoked', 'error'
                )),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_deriv_accounts_provider_account
                UNIQUE (deriv_account_id)
        )
    """)

    op.execute("""
        CREATE INDEX ix_deriv_accounts_user
        ON deriv_accounts (user_id)
    """)

    # Tentativas temporarias de autorizacao OAuth
    op.execute("""
        CREATE TABLE oauth_transactions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL
                REFERENCES platform_users(id) ON DELETE CASCADE,
            state_hash BYTEA NOT NULL UNIQUE,
            code_verifier_encrypted BYTEA NOT NULL,
            expires_at TIMESTAMPTZ NOT NULL,
            used_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE INDEX ix_oauth_transactions_user
        ON oauth_transactions (user_id)
    """)

    op.execute("""
        CREATE INDEX ix_oauth_transactions_expires
        ON oauth_transactions (expires_at)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS oauth_transactions")
    op.execute("DROP TABLE IF EXISTS deriv_accounts")
    op.execute("DROP TABLE IF EXISTS platform_users")
