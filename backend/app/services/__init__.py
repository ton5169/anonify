from app.services.base import (
    HtmlService,
    PiiRule,
    TextAnonify,
    ValidationRule,
    ValidationService,
)
from app.services.html_service import HtmlService as hs
from app.services.model_service import (
    ModelRuleAbAi,
    ModelRuleBertBase,
    RemovalServiceModel,
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

# rules
regex_rules: list[PiiRule] = [
    RegexRuleEmail(),
    RegexRuleIpv4(),
    RegexRuleIpv6(),
    RegexRuleUrl(),
]
model_rules: list[PiiRule] = [
    ModelRuleAbAi(),
    ModelRuleBertBase(),
]

validation_rules: list[ValidationRule] = [
    ValidationRuleNonEmpty(),
]

# services
html_service: HtmlService = hs()
validation_service: ValidationService = ValidationServiceChecker(rules=validation_rules)
removal_service_regex: TextAnonify = RemovalServiceRegex(rules=regex_rules)
removal_service_model: TextAnonify = RemovalServiceModel(rules=model_rules)


__all__ = [
    "validation_service",
    "removal_service_regex",
    "removal_service_model",
    "html_service",
]
