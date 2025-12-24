from app.models.core import CoreModel
from pydantic import Field


class PiiBase(CoreModel):
    original_text: str = Field(..., min_length=1, max_length=5000)


class PiiIn(PiiBase):
    pass


class PiiOut(PiiBase):
    cleaned_text: str
    method: str | None = None
    replaced_values: dict[str, str] = Field(default_factory=dict)
    replaced_count: dict[str, int] = Field(default_factory=dict)
