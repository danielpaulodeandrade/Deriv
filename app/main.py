import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.market_data import router as market_data_router
from app.core.config import settings
from app.db.connection import close_db_pool, init_db_pool
from app.services.deriv_market_data import market_data_service

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("deriv_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Starting up %s (Env: %s)",
        settings.APP_NAME,
        settings.APP_ENV,
    )

    await init_db_pool()

    try:
        await market_data_service.start()
        yield
    finally:
        logger.info("Shutting down %s", settings.APP_NAME)

        try:
            await market_data_service.stop()
        finally:
            # Always close the pool, even if service shutdown raises.
            await close_db_pool()


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend para robôs de trading e ingestão de ticks da Deriv",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(market_data_router)
