from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from app.core.config import settings
from app.db.connection import check_db_ready

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str


class ReadinessResponse(BaseModel):
    status: str
    database: str
    detail: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="API Health Check",
    description="Verifies that the API application is running and responding.",
)
async def health_check() -> HealthResponse:
    """Basic liveness probe for the API service."""
    return HealthResponse(
        status="ok",
        app=settings.APP_NAME,
        environment=settings.APP_ENV,
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={
        status.HTTP_200_OK: {"description": "All dependencies (database) are healthy."},
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Database or critical dependency is unavailable.",
            "model": ReadinessResponse,
        },
    },
    summary="Readiness Probe",
    description="Verifies that all backing services, notably PostgreSQL, are accessible.",
)
async def readiness_check(response: Response) -> ReadinessResponse:
    """Readiness probe checking database connectivity."""
    db_ok, detail = await check_db_ready()

    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            status="unhealthy",
            database="disconnected",
            detail=detail,
        )

    return ReadinessResponse(
        status="ready",
        database="connected",
        detail=detail,
    )
