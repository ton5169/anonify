import re

import pytest
from app.services.regex_service import (
    RegexRuleEmail,
    RegexRuleIpv4,
    RegexRuleIpv6,
    RegexRuleUrl,
    RemovalServiceRegex,
)
from app.services.utils import TextUtils


@pytest.fixture
def regex_service():
    rules = [RegexRuleEmail(), RegexRuleIpv4(), RegexRuleIpv6(), RegexRuleUrl()]
    return RemovalServiceRegex(rules=rules)


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
        assert result.cleaned_text == expected_result
        assert result.method == "regex"

    @pytest.mark.parametrize(
        "text, method, pattern, placeholder, expected_result",
        [
            (
                "Multiple URL here URL URL",
                "regex",
                re.compile(r"URL"),
                "URL",
                "Multiple [URL_1] here [URL_2] [URL_3]",
            ),
            (
                "Text without placeholder",
                "regex",
                re.compile(r"EMAIL"),
                "EMAIL",
                "Text without placeholder",
            ),
            (
                "One IP_ADDRESS here",
                "regex",
                re.compile(r"IP_ADDRESS"),
                "IP_ADDRESS",
                "One [IP_ADDRESS_1] here",
            ),
        ],
    )
    def test_success_return_placeholder_with_counter(
        self, text: str, method: str, pattern, placeholder: str, expected_result: str
    ) -> None:
        result, _, _ = TextUtils.return_placeholder_with_counter(
            text, method, pattern, placeholder
        )
        assert result == expected_result

    @pytest.mark.parametrize(
        "text, expected_result",
        [
            (
                "My email is fakemail@mail.com and my IP is 192.168.1.1",
                {
                    "EMAIL_1": "fakemail@mail.com",
                    "IP_ADDRESS_1": "192.168.1.1",
                },
            ),
        ],
    )
    def test_replaced_values(
        self, regex_service, text: str, expected_result: dict
    ) -> None:
        result = regex_service.replaced_values(text)
        assert result == expected_result

    @pytest.mark.parametrize(
        "text, expected_result",
        [
            (
                "My email is fakemail@mail.com and my IP is 192.168.1.1",
                {"EMAIL": 1, "IP_ADDRESS": 1},
            ),
        ],
    )
    def test_replaced_count(
        self, regex_service, text: str, expected_result: dict
    ) -> None:
        clean_result = regex_service.clean(text)
        result = regex_service.replaced_count(clean_result.cleaned_text)
        assert result == expected_result
