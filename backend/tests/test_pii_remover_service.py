import pytest
from app.services import pii_removal_regex_service as regex_removal


class TestPiiRemovalRegexService:
    @pytest.mark.parametrize(
        "original_text, clean_text",
        (
            ("My email is fakemail@mail.com", "My email is [EMAIL_1]"),
            ("My IP adress is 192.168.1.1", "My IP adress is [IP ADDRESS_1]"),
            (
                "Check my website at www.example.com",
                "Check my website at [URL_1]",
            ),
            (
                "Check my website at https://havefun.com",
                "Check my website at [URL_1]",
            ),
        ),
    )
    def test_remove_type_regex(
        self,
        original_text: str,
        clean_text: str,
    ) -> None:
        result = regex_removal.regex_clean(original_text)
        assert result[0] == clean_text
        assert result[1] == "regex"
