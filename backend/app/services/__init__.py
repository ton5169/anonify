from app.services.base import PiiRule, TextCleaner, ValidationRule, ValidationService
from app.services.regex_service import (
    RegexEmailRule,
    RegexIpv4Rule,
    RegexIpv6Rule,
    RegexUrlRule,
    RemovalServiceRegex,
)
from app.services.utils import return_placeholder_with_counter
from app.services.validation_service import ValidationServiceChecker

regex_rules: list[PiiRule] = [
    RegexEmailRule(),
    RegexIpv4Rule(),
    RegexIpv6Rule(),
    RegexUrlRule(),
]

validation_rules: list[ValidationRule] = []


validation_service: ValidationService = ValidationServiceChecker(rules=validation_rules)
removal_service_regex: TextCleaner = RemovalServiceRegex(rules=regex_rules)
