import re
from typing import Tuple


# TODO
# https://gemini.google.com/share/b21a2b6514d6
# make code improvements by using dependency injection and protocols


class PiiRemovalRegexService:
    def __init__(self):
        self.email_pattern = re.compile(
            r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
        )

        self.ipv4_pattern = re.compile(
            r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        )

        self.ipv6_pattern = re.compile(
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

        self.url_pattern = re.compile(r"\b(?:https?://|www\.)[^\s<>\"]+", re.IGNORECASE)

    @staticmethod
    def clean_pii(text: str) -> str:
        text = re.sub(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", "[REDACTED]", text)  # Names
        text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[REDACTED]", text)  # Emails
        return text

    @staticmethod
    def return_placeholder_with_counter(
        text: str, placeholder: str, number: int
    ) -> str:
        count = 0

        if not placeholder:
            raise ValueError("Placeholder cannot be None or an empty string.")

        if number < 0:
            raise ValueError("Number of occurrences must be a positive integer (>= 1).")

        def replace(match):
            nonlocal count

            if count < number:
                count += 1
                return f"[{placeholder}_{count}]"
            else:
                return match.group(0)

        modified_text = re.sub(re.escape(placeholder), replace, text)

        return modified_text

    def _clean_emails(self, text: str, placeholder: str) -> str:
        text, n = self.email_pattern.subn(placeholder, text)
        text = self.return_placeholder_with_counter(text, placeholder, n)
        return text

    def _clean_ipv4(self, text: str, placeholder: str) -> str:
        text, n = self.ipv4_pattern.subn(placeholder, text)
        text = self.return_placeholder_with_counter(text, placeholder, n)
        return text

    def _clean_ipv6(self, text: str, placeholder: str) -> str:
        text, n = self.ipv6_pattern.subn(placeholder, text)
        text = self.return_placeholder_with_counter(text, placeholder, n)
        return text

    def _clean_urls(self, text: str, placeholder: str) -> str:
        text, n = self.url_pattern.subn(placeholder, text)
        text = self.return_placeholder_with_counter(text, placeholder, n)

        return text

    def clean(self, text: str) -> Tuple[str, str]:
        text = self._clean_urls(text, "URL")
        text = self._clean_emails(text, "EMAIL")
        text = self._clean_ipv4(text, "IP_ADDRESS")
        text = self._clean_ipv6(text, "IP_ADDRESS")

        return (text, "regex")
