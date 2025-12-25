import pytest
from app.core.errors import ServiceError, ValidationError
from app.models.pii import PiiIn
from app.services.html_service import HtmlService
from app.services.orchestrator import Orchestrator
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


@pytest.fixture
def regex_service():
    rules = [RegexRuleEmail(), RegexRuleIpv4(), RegexRuleIpv6(), RegexRuleUrl()]
    return RemovalServiceRegex(rules=rules)


@pytest.fixture
def html_service():
    return HtmlService()


@pytest.fixture
def validation_service():
    return ValidationServiceChecker(rules=[ValidationRuleNonEmpty()])


class TestOrchestrator:
    def test_orchestrator_success(
        self, regex_service, validation_service, html_service
    ) -> None:
        text = "My email is test@mail.com and my IP is 192.168.1.1"

        orch = Orchestrator(
            input=PiiIn(original_text=text),
            clean_services=[regex_service],
            validation_services=[validation_service],
            html_service=html_service,
            clean_html=False,
        )

        result = orch.run_pipeline()

        assert result.cleaned_text == (
            "My email is [EMAIL_1] and my IP is [IP_ADDRESS_1]"
        )
        assert result.methods == ["regex"]
        assert result.replaced_values == {
            "regex:EMAIL_1": "test@mail.com",
            "regex:IP_ADDRESS_1": "192.168.1.1",
        }
        assert result.replaced_count == {
            "regex:EMAIL": 1,
            "regex:IP_ADDRESS": 1,
        }

    def test_orchestrator_validation_error(
        self, regex_service, validation_service, html_service
    ) -> None:
        orch = Orchestrator(
            input=PiiIn(original_text="  "),
            clean_services=[regex_service],
            validation_services=[validation_service],
            html_service=html_service,
            clean_html=False,
        )

        with pytest.raises(ValidationError):
            orch.run_pipeline()

    def test_orchestrator_no_validation_services(
        self, regex_service, html_service
    ) -> None:
        orch = Orchestrator(
            input=PiiIn(original_text="test@mail.com"),
            clean_services=[regex_service],
            validation_services=[],
            html_service=html_service,
            clean_html=False,
        )

        with pytest.raises(ServiceError, match="No validation services configured"):
            orch.run_pipeline()

    def test_orchestrator_no_clean_services(
        self, validation_service, html_service
    ) -> None:
        orch = Orchestrator(
            input=PiiIn(original_text="test@mail.com"),
            clean_services=[],
            validation_services=[validation_service],
            html_service=html_service,
            clean_html=False,
        )

        with pytest.raises(ServiceError, match="No clean services configured"):
            orch.run_pipeline()

    def test_orchestrator_clean_html_applied(
        self, regex_service, validation_service, html_service
    ) -> None:
        html_text = "<p>My email is test@mail.com</p>"

        orch = Orchestrator(
            input=PiiIn(original_text=html_text),
            clean_services=[regex_service],
            validation_services=[validation_service],
            html_service=html_service,
            clean_html=True,
        )

        result = orch.run_pipeline()

        assert "[EMAIL_1]" in result.cleaned_text
        assert "<p>" not in result.cleaned_text
        assert result.methods == ["regex"]

    @pytest.mark.parametrize(
        "text, expected_count",
        [
            (
                "Emails: a@mail.com and b@mail.com",
                {"regex:EMAIL": 2},
            ),
        ],
    )
    def test_orchestrator_replaced_count_multiple(
        self, regex_service, validation_service, html_service, text, expected_count
    ) -> None:
        orch = Orchestrator(
            input=PiiIn(original_text=text),
            clean_services=[regex_service],
            validation_services=[validation_service],
            html_service=html_service,
            clean_html=False,
        )

        result = orch.run_pipeline()
        assert result.replaced_count == expected_count
