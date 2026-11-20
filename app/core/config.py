from pydantic import computed_field
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
    POSTGRES_PASSWORD: str = "deriv_pass"
    POSTGRES_MIN_POOL_SIZE: int = 2
    POSTGRES_MAX_POOL_SIZE: int = 10
    POSTGRES_TIMEOUT_SECONDS: float = 5.0

    # Deriv market data
    DERIV_WS_URL: str = "wss://api.derivws.com/trading/v1/options/ws/public"
    DERIV_SYMBOLS: str = "1HZ100V"
    DERIV_RECONNECT_DELAY_SECONDS: float = 2.0
    DERIV_BATCH_SIZE: int = 500
    DERIV_FLUSH_INTERVAL_SECONDS: float = 0.5

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
