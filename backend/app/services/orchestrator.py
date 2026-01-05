from typing import List

from app.core.errors import ServiceError, ValidationError
from app.models.pii import PiiIn, PiiOut
from app.services.base import HtmlService, TextAnonify, ValidationService


class Orchestrator:
    def __init__(
        self,
        input: PiiIn,
        clean_services: List[TextAnonify],
        validation_services: List[ValidationService],
        html_service: HtmlService,
        clean_html: bool = False,
    ) -> None:
        self.input = input
        self.clean_services = clean_services
        self.validation_services = validation_services
        self.html_service = html_service
        self.clean_html = clean_html

    def run_pipeline(self) -> PiiOut:
        text = self.input.original_text

        if self.clean_html:
            text = self.html_service.clean(text)
            self.input = PiiIn(original_text=text)

        if not self.validation_services:
            raise ServiceError("No validation services configured")

        for vs in self.validation_services:
            is_valid, msg = vs.validate(text)
            if not is_valid:
                raise ValidationError(msg)

        if not self.clean_services:
            raise ServiceError("No clean services configured")

        methods: list[str] = []
        replaced_values: dict[str, str] = {}
        replaced_count: dict[str, int] = {}

        try:
            for service in self.clean_services:
                result = service.clean(text)

                text = result.cleaned_text
                methods.append(result.method)

                replaced_values.update(result.replaced_values)
                replaced_count.update(result.replaced_count)
        except Exception as e:
            raise ServiceError(
                f"An error occurred during service {service.__class__.__name__}: {e}"
            ) from e

        return PiiOut(
            original_text=self.input.original_text,
            cleaned_text=text,
            methods=methods,
            replaced_values=replaced_values,
            replaced_count=replaced_count,
        )
