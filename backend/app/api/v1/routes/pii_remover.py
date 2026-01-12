import logging

from app.core.errors import ServiceError, ValidationError
from app.models.pii import PiiIn, PiiOut
from app.services import (
    html_service,
    removal_service_model,
    removal_service_regex,
    validation_service,
)
from app.services.orchestrator import Orchestrator
from fastapi import APIRouter, HTTPException
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

logger = logging.getLogger("anonify")


router = APIRouter()


@router.post("/clean", name="pii:remover", status_code=HTTP_200_OK)
def remove_pii(
    input: PiiIn,
    clean_html: bool = False,
) -> PiiOut:
    orchestrator = Orchestrator(
        input=input,
        clean_services=[removal_service_regex, removal_service_model],
        validation_services=[validation_service],
        html_service=html_service,
        clean_html=clean_html,
    )

    try:
        cleaned_result = orchestrator.run_pipeline()
    except ValidationError as ve:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=ve.message)
    except ServiceError as se:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=se.message
        )

    return PiiOut(
        original_text=input.original_text,
        cleaned_text=cleaned_result.cleaned_text,
        methods=cleaned_result.methods,
        replaced_values=cleaned_result.replaced_values,
        replaced_count=cleaned_result.replaced_count,
    )
