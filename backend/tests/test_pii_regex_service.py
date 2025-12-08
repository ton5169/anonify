import re

import pytest
from app.services import removal_service_regex, return_placeholder_with_counter


@pytest.fixture
def regex_service():
    return removal_service_regex


class TestRegexService:
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
        regex_service,
        original_text: str,
        expected_result: str,
    ) -> None:
        result = regex_service.clean(original_text)
        assert result[0] == expected_result
        assert result[1] == "regex"

    @pytest.mark.parametrize(
        "text, pattern, placeholder, expected_result",
        [
            (
                "Multiple URL here URL URL",
                re.compile(r"URL"),
                "URL",
                "Multiple [URL_1] here [URL_2] [URL_3]",
            ),
            (
                "Text without placeholder",
                re.compile(r"EMAIL"),
                "EMAIL",
                "Text without placeholder",
            ),
            (
                "One IP_ADDRESS here",
                re.compile(r"IP_ADDRESS"),
                "IP_ADDRESS",
                "One [IP_ADDRESS_1] here",
            ),
        ],
    )
    def test_success_return_placeholder_with_counter(
        self, text: str, pattern, placeholder: str, expected_result: str
    ) -> None:
        result = return_placeholder_with_counter(text, pattern, placeholder)
        assert result == expected_result
