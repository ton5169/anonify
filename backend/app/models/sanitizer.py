from app.models.core import CoreModel


class SanitizerBase(CoreModel):
    original_text: str


class SanitizerIn(SanitizerBase):
    pass


class SanitizerOut(SanitizerBase):
    sanitized_text: str
    sanitizer_type: str | None = None
