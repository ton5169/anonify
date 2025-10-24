from typing import Annotated

from app.core.config import MAX_TEXT_LENGTH
from app.models.sanitizer import SanitizerOut
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/", response_model=SanitizerOut, name="sanitizer:get-clean-text")
async def get_clean_text(
    text: Annotated[str | None, Query(max_length=MAX_TEXT_LENGTH)] = None,
) -> SanitizerOut:
    return SanitizerOut(
        original_text=text or "",
        sanitized_text="This is some sanitized text.",
        sanitizer_type="basic",
    )
