from dataclasses import dataclass
from typing import Dict, Protocol, Tuple


@dataclass
class RuleResult:
    """Class to hold the result of applying a PII rule."""

    text: str
    replaced_values: Dict[str, str]
    replaced_count: Dict[str, int]

@dataclass
class CleanedTextResult:
    """Class to hold the result of cleaning text."""

    method: str
    cleaned_text: str
    replaced_values: Dict[str, str]
    replaced_count: Dict[str, int]


class HtmlService(Protocol):
    """Protocol for HTML processing service."""

    def clean(self, html: str) -> str:
        """Cleans the input HTML and returns the cleaned HTML."""
        ...

    def restore(self, text: str) -> str:
        """Restores the cleaned text back to HTML format."""
        ...


class ValidationService(Protocol):
    """Protocol for validation service."""

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


class TextAnonify(Protocol):
    """Protocol for text cleaning services."""

    def clean(self, text: str) -> CleanedTextResult:
        """Cleans the input text and returns the cleaned text along with the method used."""
        ...

    def replaced_values(self, text: str) -> Dict[str, str]:
        """Returns a dictionary of replaced values in the cleaned text."""
        ...

    def replaced_count(self, text: str) -> Dict[str, int]:
        """Returns a dictionary of counts of replaced values in the cleaned text."""
        ...


class PiiRule(Protocol):
    """Protocol for PII removal rules."""

    @property
    def placeholder(self) -> str:
        """Returns the placeholder used for this PII type."""
        ...

    def apply(self, text: str, method: str) -> str:
        """Applies the PII removal rule to the input text."""
        ...

    def replaced_values(self, text: str, method: str) -> dict[str, str]:
        """Returns a dictionary of replaced values for this PII type."""
        ...

    def replaced_count(self, text: str, method: str) -> dict[str, int]:
        """Returns a dictionary of counts of replaced values for this PII type."""
        ...
