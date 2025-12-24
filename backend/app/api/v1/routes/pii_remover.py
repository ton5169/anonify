from app.models.pii import PiiIn, PiiOut
from app.services import removal_service_regex
from fastapi import APIRouter
from starlette.status import HTTP_201_CREATED

router = APIRouter()


@router.post("/clean", name="pii:remover", status_code=HTTP_201_CREATED)
async def remove_pii(input: PiiIn) -> PiiOut:
    cleaned_result = removal_service_regex.clean(input.original_text)
    return PiiOut(
        original_text=input.original_text,
        cleaned_text=cleaned_result.cleaned_text,
        method=cleaned_result.method,
        replaced_values=cleaned_result.replaced_values,
        replaced_count=cleaned_result.replaced_count,
    )
