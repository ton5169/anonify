from typing import Protocol, Tuple


class ValidationService(Protocol):
    """Protocol for validation services."""

    def validate(self, text: str) -> Tuple[bool, str]:
        """Validates the input text and returns a tuple of (is_valid, message)."""
        ...


class ValidationRule(Protocol):
    """Protocol for validation rules."""

    def check(self, text: str) -> bool:
        """Checks the input text against the validation rule."""
        ...

    def description(self) -> str:
        """Returns a description of the validation rule."""
        ...


class TextCleaner(Protocol):
    """Protocol for text cleaning services."""

    def clean(self, text: str) -> Tuple[str, str]:
        """Cleans the input text and returns the cleaned text along with the method used."""
        ...


class PiiRule(Protocol):
    """Protocol for PII removal rules."""

    def apply(self, text: str) -> str:
        """Applies the PII removal rule to the input text."""
        ...

    @property
    def placeholder(self) -> str:
        """Returns the placeholder used for this PII type."""
        ...
