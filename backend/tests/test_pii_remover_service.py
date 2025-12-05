import pytest
from app.services import pii_removal_regex_service as regex_service


class TestPiiRemovalRegexService:
    @pytest.mark.parametrize(
        "original_text, expected_result",
        (
            ("My email is fakemail@mail.com", "My email is [EMAIL_1]"),
            ("My IP adress is 192.168.1.1", "My IP adress is [IP_ADDRESS_1]"),
            (
                "Check my website at www.example.com",
                "Check my website at [URL_1]",
            ),
            (
                "Check my website at https://havefun.com",
                "Check my website at [URL_1]",
            ),
            (
                "Check my websites at https://havefun.com and https://havefun2.com",
                "Check my websites at [URL_1] and [URL_2]",
            ),
        ),
    )
    def test_remove_type_regex(
        self,
        original_text: str,
        expected_result: str,
    ) -> None:
        result = regex_service.clean(original_text)
        assert result[0] == expected_result
        assert result[1] == "regex"

    @pytest.mark.parametrize(
        "text, placeholder, number, expected_result",
        [
            (
                "Multiple URL here URL URL",
                "URL",
                3,
                "Multiple [URL_1] here [URL_2] [URL_3]",
            ),
            ("Text without placeholder", "EMAIL", 0, "Text without placeholder"),
            ("One IP_ADDRESS here", "IP_ADDRESS", 1, "One [IP_ADDRESS_1] here"),
            ("URL URL URL URL", "URL", 2, "[URL_1] [URL_2] URL URL"),
        ],
    )
    def test_success_return_placeholder_with_counter(
        self, text: str, placeholder: str, number: int, expected_result: str
    ) -> None:
        result = regex_service.return_placeholder_with_counter(
            text, placeholder, number
        )
        assert result == expected_result

    @pytest.mark.parametrize(
        "text, placeholder, number, exception_message",
        [
            (
                "Text with empty placeholder",
                "",
                2,
                "Placeholder cannot be None or an empty string.",
            ),
            (
                "Text with None placeholder",
                None,
                1,
                "Placeholder cannot be None or an empty string.",
            ),
            (
                "Text with negative number [URL]",
                "URL",
                -1,
                "Number of occurrences must be a positive integer (>= 1).",
            ),
        ],
    )
    def test_error_return_placeholder_with_counter(
        self, text: str, placeholder: str, number: int, exception_message: str
    ) -> None:
        with pytest.raises(ValueError) as excinfo:
            regex_service.return_placeholder_with_counter(text, placeholder, number)
        assert exception_message in str(excinfo.value)
