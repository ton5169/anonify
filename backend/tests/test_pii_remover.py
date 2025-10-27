import pytest
from app.models.pii import PiiOut
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

pytestmark = pytest.mark.asyncio


@pytest.fixture
def pii_out():
    return PiiOut(
        original_text="My name is John Doe and my email is fakemail@mail.com.",
        clean_text="My name is [REDACTED] and my email is [REDACTED].",
        clean_method="regex",
    )


class TestPiiRemoverRoutes:
    async def test_pii_remover_route_exists(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        res = await client.post(
            app.url_path_for("pii:remover"),
            json={
                "original_text": "My name is John Doe and my email is fakemail@mail.com."
            },
        )
        assert res.status_code != HTTP_404_NOT_FOUND

    async def test_pii_remover_valid_input(
        self, app: FastAPI, client: AsyncClient, pii_out: PiiOut
    ) -> None:
        res = await client.post(
            app.url_path_for("pii:remover"),
            json={"original_text": pii_out.original_text},
        )
        assert res.status_code == HTTP_201_CREATED

        input = PiiOut(**res.json())
        assert input == pii_out

    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (
            (None, 422),
            ({}, 422),
            (12345, 422),
            ("", 422),
            ([], 422),
            ("a" * 5001, 422),
            ({"name": "John"}, 422),
        ),
    )
    async def test_pii_remover_invalid_input_raises_error(
        self, app: FastAPI, client: AsyncClient, invalid_payload: dict, status_code: int
    ) -> None:
        res = await client.post(
            app.url_path_for("pii:remover"), json={"original_text": invalid_payload}
        )
        assert res.status_code == status_code
