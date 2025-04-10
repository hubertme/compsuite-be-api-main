import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio

async def test_health_check_endpoint(async_client: AsyncClient, db_session: AsyncSession):
    response = await async_client.get("/api/v1/health/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "environment" in data
    assert "database" in data
    assert "redis" in data
    
    # Check specific values
    assert data["status"] in ["healthy", "unhealthy"]
    assert isinstance(data["version"], str)
    assert data["environment"] in ["development", "staging", "production"]
    assert data["database"] in ["connected", "disconnected"]
    assert data["redis"] in ["connected", "disconnected"]

async def test_health_check_database_connection(async_client: AsyncClient, db_session: AsyncSession):
    response = await async_client.get("/api/v1/health/health")
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "connected"

async def test_health_check_redis_connection(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health/health")
    assert response.status_code == 200
    data = response.json()
    assert data["redis"] == "connected"
