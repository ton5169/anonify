import re


class PiiRemovalService:
    @staticmethod
    def clean_pii(text: str) -> str:
        text = re.sub(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", "[REDACTED]", text)  # Names
        text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[REDACTED]", text)  # Emails
        return text
