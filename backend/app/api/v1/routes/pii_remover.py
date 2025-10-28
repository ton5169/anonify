from app.models.pii import PiiIn, PiiOut
from app.services import pii_removal_regex_service
from fastapi import APIRouter
from starlette.status import HTTP_201_CREATED

router = APIRouter()


@router.post("/clean", name="pii:remover", status_code=HTTP_201_CREATED)
async def remove_pii(input: PiiIn) -> PiiOut:
    clean_text = pii_removal_regex_service.clean_pii(input.original_text)
    return PiiOut(
        original_text=input.original_text,
        clean_text=clean_text,
        clean_method="regex",
    )
