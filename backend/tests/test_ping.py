import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.status import (
    HTTP_404_NOT_FOUND,
)

pytestmark = pytest.mark.asyncio

class TestPingRoutes:
    async def test_ping_returns_pong(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.get(app.url_path_for("ping"))
        assert res.status_code != HTTP_404_NOT_FOUND
        assert res.status_code == 200
        assert res.json() == {"message": "pong"}
