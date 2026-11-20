
from fastapi import APIRouter

from app.services.deriv_market_data import market_data_service

router = APIRouter(
    prefix="/market-data",
    tags=["Market Data"],
)


@router.get("/health")
async def market_data_health():
    return market_data_service.get_status()
