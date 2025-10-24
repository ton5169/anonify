import os

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


# Fixture to create FastAPI app instance for testing
@pytest.fixture
def app() -> FastAPI:
    from app.api.server import get_application

    return get_application()


# Set up environment variables for testing
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    os.environ["AUTH_PASSWORD"] = "test_password"
    os.environ["MAX_TEXT_LENGTH"] = "1500"


# Fixture to create an AsyncClient for testing
@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncClient:  # type: ignore
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
            headers={"Content-Type": "application/json"},
        ) as client:
            yield client  # type: ignore
