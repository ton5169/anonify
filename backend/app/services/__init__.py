from app.services.base import (
    PiiRule,
    TextAnonify,
    ValidationRule,
    ValidationService,
    HtmlService,
)
from app.services.regex_service import (
    RegexRuleEmail,
    RegexRuleIpv4,
    RegexRuleIpv6,
    RegexRuleUrl,
    RemovalServiceRegex,
)
from app.services.validation_service import (
    ValidationRuleNonEmpty,
    ValidationServiceChecker,
)

from app.services.html_service import HtmlService as hs

# rules
regex_rules: list[PiiRule] = [
    RegexRuleEmail(),
    RegexRuleIpv4(),
    RegexRuleIpv6(),
    RegexRuleUrl(),
]
validation_rules: list[ValidationRule] = [
    ValidationRuleNonEmpty(),
]

# services
html_service: HtmlService = hs()
validation_service: ValidationService = ValidationServiceChecker(rules=validation_rules)
removal_service_regex: TextAnonify = RemovalServiceRegex(rules=regex_rules)


__all__ = ["validation_service", "removal_service_regex"]
