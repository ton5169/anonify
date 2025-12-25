import re
from abc import ABC, abstractmethod
from typing import Tuple

from app.services.base import CleanedTextResult, PiiRule, RuleResult, TextAnonify
from app.services.utils import TextUtils


class BaseRegexRule(PiiRule, ABC):
    _pattern: re.Pattern[str]

    @property
    @abstractmethod
    def placeholder(self) -> str: ...

    def _apply_rule_and_get_replaced_values(self, text: str, method: str) -> RuleResult:
        text, replaced_values = TextUtils.return_placeholder_with_counter(
            text,
            method,
            self._pattern,
            self.placeholder,
        )
        return RuleResult(text, replaced_values)

    def apply(self, text: str, method: str = "regex") -> str:
        return self._apply_rule_and_get_replaced_values(text, method).text

    def replaced_values(self, text: str, method: str = "regex") -> dict[str, str]:
        return self._apply_rule_and_get_replaced_values(text, method).replaced_values
class RegexRuleEmail(BaseRegexRule):
    def __init__(self):
        self._pattern = re.compile(
            r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
        )

    @property
    def placeholder(self) -> str:
        return "EMAIL"


class RegexRuleIpv4(BaseRegexRule):
    def __init__(self):
        self._pattern = re.compile(
            r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        )

    @property
    def placeholder(self) -> str:
        return "IP_ADDRESS"


class RegexRuleIpv6(BaseRegexRule):
    def __init__(self):
        self._pattern = re.compile(
            r"\b(?:(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|"
            r"(?:[0-9a-fA-F]{1,4}:){1,7}:|"
            r"(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|"
            r"(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|"
            r"(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|"
            r"(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|"
            r"(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|"
            r"[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|"
            r":(?:(?::[0-9a-fA-F]{1,4}){1,7}|:))\b",
            re.IGNORECASE,
        )

    @property
    def placeholder(self) -> str:
        return "IP_ADDRESS"


class RegexRuleUrl(BaseRegexRule):
    def __init__(self):
        self._pattern = re.compile(r"\b(?:https?://|www\.)[^\s<>\"]+", re.IGNORECASE)

    @property
    def placeholder(self) -> str:
        return "URL"


class RemovalServiceRegex(TextAnonify):
    def __init__(self, rules: list[PiiRule]):
        self._rules = rules
        self._method = "regex"

    def _apply_rules(self, text: str) -> Tuple[str, str]:
        cleaned_text = text
        for rule in self._rules:
            cleaned_text = rule.apply(cleaned_text, self._method)

        return cleaned_text, self._method

    def replaced_count(self, text: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for rule in self._rules:
            pattern = re.compile(rf"\[{rule.placeholder}_(\d+)\]", re.IGNORECASE)
            unique_matches = set(pattern.findall(text))
            if unique_matches:
                counts[rule.placeholder] = len(unique_matches)

        return counts

    def replaced_values(self, text: str) -> dict[str, str]:
        all_replaced_values: dict[str, str] = {}
        for rule in self._rules:
            replaced_values = rule.replaced_values(text, self._method)
            all_replaced_values.update(replaced_values)

        return all_replaced_values

    def clean(self, text: str) -> CleanedTextResult:
        cleaned_text, method = self._apply_rules(text)
        replaced_values = self.replaced_values(text)
        replaced_count = self.replaced_count(cleaned_text)

        return CleanedTextResult(
            method=method,
            cleaned_text=cleaned_text,
            replaced_values=replaced_values,
            replaced_count=replaced_count,
        )
