import pytest
from app.services import validation_service as vs


@pytest.fixture
def validation_service():
    return vs


class TestValidationService:
    @pytest.mark.parametrize(
        "original_text, expected_result",
        [
            ("Original text 1", (True, "Original text 1")),
        ],
    )
    def test_return_valid_text(
        self, validation_service, original_text: str, expected_result: str
    ) -> None:
        result = validation_service.validate(original_text)
        assert result == expected_result
