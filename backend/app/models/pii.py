from app.models.core import CoreModel
from pydantic import Field


class PiiBase(CoreModel):
    original_text: str = Field(..., min_length=1, max_length=5000)


class PiiIn(PiiBase):
    pass


class PiiOut(PiiBase):
    clean_text: str
    clean_method: str | None = None
