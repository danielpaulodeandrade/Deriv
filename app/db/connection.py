import asyncio
import logging
from typing import Optional
import asyncpg
from app.core.config import settings

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def init_db_pool() -> Optional[asyncpg.Pool]:
    """Initialize the asynchronous PostgreSQL connection pool."""
    global _pool
    if _pool is not None:
        return _pool

    try:
        logger.info(
            "Initializing database connection pool to %s:%s/%s",
            settings.POSTGRES_HOST,
            settings.POSTGRES_PORT,
            settings.POSTGRES_DB,
        )
        _pool = await asyncpg.create_pool(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            min_size=settings.POSTGRES_MIN_POOL_SIZE,
            max_size=settings.POSTGRES_MAX_POOL_SIZE,
            command_timeout=settings.POSTGRES_TIMEOUT_SECONDS,
        )
        logger.info("Database connection pool established successfully.")
        return _pool
    except Exception as exc:
        logger.warning(
            "Failed to initialize database connection pool on startup: %s. "
            "Will retry on health/readiness probe.",
            exc,
        )
        _pool = None
        return None


async def close_db_pool() -> None:
    """Close the asynchronous PostgreSQL connection pool gracefully."""
    global _pool
    if _pool is not None:
        logger.info("Closing database connection pool.")
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed.")


def get_db_pool() -> Optional[asyncpg.Pool]:
    """Get the current database connection pool instance."""
    return _pool


async def check_db_ready() -> tuple[bool, str]:
    """Check if PostgreSQL is accessible and responding to queries.
    Returns:
        tuple[bool, str]: (is_ready, message_or_error)
    """
    global _pool
    if _pool is None:
        # Tenta inicializar se ainda não estava ativo
        pool = await init_db_pool()
        if pool is None:
            return False, "Database connection pool is not initialized"

    try:
        async with _pool.acquire(timeout=settings.POSTGRES_TIMEOUT_SECONDS) as conn:
            result = await conn.fetchval("SELECT 1")
            if result == 1:
                return True, "Database is connected and healthy"
            return False, f"Unexpected ping result: {result}"
    except Exception as exc:
        logger.error("Database readiness check failed: %s", exc)
        return False, str(exc)
