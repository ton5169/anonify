from app.services.base import ValidationRule


class ValidationServiceChecker:
    def __init__(self, rules: list[ValidationRule]):
        self._rules = rules

    def validate(self, text: str) -> tuple[bool, str]:
        for rule in self._rules:
            if not rule.check(text):
                return (False, f"Validation failed for rule: {rule.__class__.__name__}")
        return (True, text)
