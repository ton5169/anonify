from app.services.base import ValidationRule


class ValidationServiceChecker:
    def __init__(self, rules: list[ValidationRule]):
        self._rules = rules

    def validate(self, text: str) -> tuple[bool, str]:
        for rule in self._rules:
            if not rule.check(text):
                return (False, f"Validation failed: {rule.description()}")
        return (True, text)

class ValidationRuleNonEmpty(ValidationRule):
    def check(self, text: str) -> bool:
        return bool(text and text.strip())

    def description(self) -> str:
        return "Input text is empty."
