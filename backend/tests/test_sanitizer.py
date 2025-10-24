import os

import pytest
from app.models.sanitizer import SanitizerIn
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_CONTENT,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture
def sanitize_in():
    return SanitizerIn(original_text="This is some original text.")


class TestGetSanizer:
    async def test_sanitizer_routes(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.get(app.url_path_for("sanitizer:get-clean-text"))
        assert res.status_code != HTTP_404_NOT_FOUND
        assert res.status_code == HTTP_200_OK

    async def test_text_length_validation_rejects_max_length(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "1500"))
        text = "a" * (MAX_TEXT_LENGTH + 1)
        res = await client.get(
            app.url_path_for("sanitizer:get-clean-text"), params={"text": text}
        )
        assert res.status_code == HTTP_422_UNPROCESSABLE_CONTENT
