import re
from typing import Tuple


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

    def _clean_regex_emails(self, text: str) -> str:
        return self.email_pattern.sub("[EMAIL_1]", text)

    def _clean_regex_ips(self, text: str) -> str:
        text = self.ipv4_pattern.sub("[IP ADDRESS_1]", text)
        text = self.ipv6_pattern.sub("[IP ADDRESS_1]", text)
        return text

    def _clean_regex_urls(self, text: str) -> str:
        return self.url_pattern.sub("[URL_1]", text)

    def regex_clean(self, text: str) -> Tuple[str, str]:
        text = self._clean_regex_urls(text)
        text = self._clean_regex_emails(text)
        text = self._clean_regex_ips(text)

        return (text, "regex")
