import re
from typing import Protocol, Tuple

# TODO
# break into multiple files
# add validation protocols


def return_placeholder_with_counter(text: str, pattern, placeholder: str) -> str:
    """Utility to replace matches and number the placeholders."""

    def replace_with_counter(match):
        nonlocal count
        count += 1
        return f"[{placeholder}_{count}]"

    temp_placeholder = f"__TEMP__{placeholder}__"
    text, n = pattern.subn(temp_placeholder, text)

    count = 0
    if n > 0:
        text = re.sub(re.escape(temp_placeholder), replace_with_counter, text)

    return text


class TextCleaner(Protocol):
    """Protocol for text cleaning services."""

    def clean(self, text: str) -> Tuple[str, str]:
        """Cleans the input text and returns the cleaned text along with the method used."""
        ...


class PiiRule(Protocol):
    """Protocol for PII removal rules."""

    def apply(self, text: str) -> str:
        """Applies the PII removal rule to the input text."""
        ...

    @property
    def placeholder(self) -> str:
        """Returns the placeholder used for this PII type."""
        ...


class RegexEmailRule:
    def __init__(self):
        self._pattern = re.compile(
            r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
        )

    @property
    def placeholder(self) -> str:
        return "EMAIL"

    def apply(self, text: str) -> str:
        return return_placeholder_with_counter(
            text,
            self._pattern,
            self.placeholder,
        )


class RegexIpv4Rule:
    def __init__(self):
        self._pattern = re.compile(
            r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        )

    @property
    def placeholder(self) -> str:
        return "IP_ADDRESS"

    def apply(self, text: str) -> str:
        return return_placeholder_with_counter(
            text,
            self._pattern,
            self.placeholder,
        )


class RegexIpv6Rule:
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

    def apply(self, text: str) -> str:
        return return_placeholder_with_counter(
            text,
            self._pattern,
            self.placeholder,
        )


class RegexUrlRule:
    def __init__(self):
        self._pattern = re.compile(r"\b(?:https?://|www\.)[^\s<>\"]+", re.IGNORECASE)

    @property
    def placeholder(self) -> str:
        return "URL"

    def apply(self, text: str) -> str:
        return return_placeholder_with_counter(
            text,
            self._pattern,
            self.placeholder,
        )


class RemovalServiceRegex:
    def __init__(self, rules: list[PiiRule]):
        self._rules = rules
        self._method_id = "regex"

    def clean(self, text: str) -> Tuple[str, str]:
        cleaned_text = text
        for rule in self._rules:
            cleaned_text = rule.apply(cleaned_text)

        return cleaned_text, self._method_id
