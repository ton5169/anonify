import pytest
from app.services.validation_service import (
    ValidationRuleNonEmpty,
    ValidationServiceChecker,
)


@pytest.fixture
def validation_service():
    return ValidationServiceChecker(rules=[ValidationRuleNonEmpty()])


class TestValidationService:
    @pytest.mark.parametrize(
        "original_text, expected_result",
        [
            ("Original text 1", (True, "Original text 1")),
            ("", (False, "Validation failed: Input text is empty.")),
            (None, (False, "Validation failed: Input text is empty.")),
            ("       ", (False, "Validation failed: Input text is empty.")),
        ],
    )
    def test_return_valid_text(
        self, validation_service, original_text: str, expected_result: str
    ) -> None:
        result = validation_service.validate(original_text)
        assert result == expected_result
