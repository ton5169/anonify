import pytest
from app.services.html_service import HtmlService


@pytest.fixture
def html_service():
    return HtmlService()


HTML_CLEAN_CASES = [
    (
        "<p>This is a <b>bold</b> statement.</p>",
        "This is a bold statement.",
        "<p>This is a <b>bold</b> statement.</p>",
    ),
]


class TestHtmlService:
    @pytest.mark.parametrize(
        "original_text, clean_result, restored_result", HTML_CLEAN_CASES
    )
    def test_clean_text_from_html(
        self, html_service, original_text: str, clean_result: str, restored_result: str
    ) -> None:
        cleaned_result = html_service.clean(original_text)
        assert cleaned_result == clean_result

    @pytest.mark.parametrize(
        "original_text, clean_result, restored_result", HTML_CLEAN_CASES
    )
    def test_restore_text_to_html(
        self, html_service, original_text: str, clean_result: str, restored_result: str
    ) -> None:
        html_service.clean(original_text)
        restored = html_service.restore(clean_result)
        assert restored == restored_result

    def test_restore_without_cleaning_raises_error(self, html_service) -> None:
        with pytest.raises(ValueError, match="No state available to restore HTML."):
            html_service.restore("Some cleaned text")
