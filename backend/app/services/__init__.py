from app.services.pii_removal import (
    PiiRule,
    RegexEmailRule,
    RegexIpv4Rule,
    RegexIpv6Rule,
    RegexUrlRule,
    RemovalServiceRegex,
    TextCleaner,
    return_placeholder_with_counter,
)

regex_rules: list[PiiRule] = [
    RegexEmailRule(),
    RegexIpv4Rule(),
    RegexIpv6Rule(),
    RegexUrlRule(),
]

removal_service_regex: TextCleaner = RemovalServiceRegex(rules=regex_rules)
