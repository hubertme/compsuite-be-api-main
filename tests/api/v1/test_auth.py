import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.user import User
from app.repositories.user import UserRepository
from app.core.security import get_password_hash

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    user_repo = UserRepository(db_session)
    user = await user_repo.create({
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword"),
        "is_active": True,
    })
    return user

async def test_login_success(async_client: AsyncClient, test_user: User):
    response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

async def test_login_invalid_password(async_client: AsyncClient, test_user: User):
    response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["message"] == "Incorrect email or password"

async def test_refresh_token(async_client: AsyncClient, test_user: User):
    # First get tokens through login
    login_response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Then try to refresh
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
