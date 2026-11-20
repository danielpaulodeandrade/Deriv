from unittest.mock import AsyncMock, patch
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check_returns_ok():
    """Verify that GET /health returns 200 OK and valid status payload."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "app" in data
        assert "environment" in data


@pytest.mark.asyncio
async def test_readiness_check_healthy():
    """Verify that GET /ready returns 200 when database connectivity is healthy."""
    with patch(
        "app.api.routes.health.check_db_ready",
        new_callable=AsyncMock,
        return_value=(True, "Database is connected and healthy"),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/ready")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            assert data["database"] == "connected"
            assert "healthy" in data["detail"]


@pytest.mark.asyncio
async def test_readiness_check_unhealthy():
    """Verify that GET /ready returns 503 when database is unavailable."""
    with patch(
        "app.api.routes.health.check_db_ready",
        new_callable=AsyncMock,
        return_value=(False, "Connection refused to PostgreSQL host"),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/ready")
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"
            assert "Connection refused" in data["detail"]
