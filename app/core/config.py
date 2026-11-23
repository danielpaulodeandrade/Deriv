
from pydantic import computed_field, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API
    APP_NAME: str = "Deriv Trading Backend"
    APP_ENV: str = "development"
    DEBUG: bool = False
    PORT: int = 8000

    # PostgreSQL Database
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "deriv_db"
    POSTGRES_USER: str = "deriv_user"
    POSTGRES_PASSWORD: str
    POSTGRES_MIN_POOL_SIZE: int = 2
    POSTGRES_MAX_POOL_SIZE: int = 10
    POSTGRES_TIMEOUT_SECONDS: float = 5.0

    # Deriv Market Data
    DERIV_WS_URL: str = "wss://api.derivws.com/trading/v1/options/ws/public"
    DERIV_RECONNECT_DELAY_SECONDS: float = 2.0
    DERIV_BATCH_SIZE: int = 500
    DERIV_FLUSH_INTERVAL_SECONDS: float = 0.5
    DERIV_SYMBOLS: str = "1HZ100V,R_100"

    # Deriv OAuth2
    DERIV_OAUTH_CLIENT_ID: str = ""
    DERIV_OAUTH_REDIRECT_URI: str = (
        "http://localhost:8000/auth/deriv/callback"
    )
    DERIV_OAUTH_SCOPE: str = "trade"
    DERIV_OAUTH_AUTH_URL: str = (
        "https://auth.deriv.com/oauth2/auth"
    )
    DERIV_OAUTH_TOKEN_URL: str = (
        "https://auth.deriv.com/oauth2/token"
    )

    # Platform Authentication
    JWT_SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_MINUTES: int = 15

    # Data Encryption
    DATA_ENCRYPTION_KEY: str

    # Email Verification
    EMAIL_VERIFICATION_TOKEN_MINUTES: int = 1440

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
