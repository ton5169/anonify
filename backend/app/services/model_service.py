import os
from typing import Any, Dict, List, Tuple

from app.services.base import CleanedTextResult, PiiRule, RuleResult
from app.services.utils import TextUtils
from transformers import pipeline


class ModelRuleAbAi(PiiRule):
    @property
    def placeholder(self) -> str:
        return "ab_ai_model"

    def _apply_rule_and_get_replaced_values(
        self, text: str, entities: List[Dict[str, Any]]
    ) -> RuleResult:
        text, replaced_count, replaced_values = TextUtils.redact_entities_with_counter(
            text, entities
        )

        return RuleResult(text, replaced_values, replaced_count)

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        pii_ner = pipeline(
            task="token-classification",
            model="ab-ai/pii_model",
            tokenizer="ab-ai/pii_model",
            token=os.getenv("HF_TOKEN", ""),
            aggregation_strategy="simple",  # groups subword tokens into spans
        )

        entities = pii_ner(text)

        return entities

    def apply(self, text: str, method: str = "ab_ai_model") -> str:
        return self._apply_rule_and_get_replaced_values(
            text, self.extract_entities(text)
        ).text

    def replaced_values(self, text: str, method: str = "ab_ai_model") -> dict[str, str]:
        return self._apply_rule_and_get_replaced_values(
            text, self.extract_entities(text)
        ).replaced_values

    def replaced_count(self, text: str, method: str = "ab_ai_model") -> dict[str, int]:
        return self._apply_rule_and_get_replaced_values(
            text, self.extract_entities(text)
        ).replaced_count


class RemovalServiceModel:
    def __init__(self, rules: list[PiiRule]) -> None:
        self._rules = rules
        self._method = "model"

    def _apply_rules(self, text: str) -> Tuple[str, str]:
        cleaned_text = text
        for rule in self._rules:
            cleaned_text = rule.apply(cleaned_text, self._method)

        return cleaned_text, self._method

    def replaced_values(self, text: str) -> Dict[str, str]:
        all_replaced_values: Dict[str, str] = {}
        for rule in self._rules:
            replaced_values = rule.replaced_values(text, self._method)
            all_replaced_values.update(replaced_values)

        return all_replaced_values

    def replaced_count(self, text: str) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for rule in self._rules:
            replaced_count = rule.replaced_count(text, self._method)
            counts.update(replaced_count)
        return counts

    def clean(self, text: str) -> CleanedTextResult:
        cleaned_text, method = self._apply_rules(text)
        replaced_values = self.replaced_values(text)
        replaced_count = self.replaced_count(text)

        return CleanedTextResult(
            method=method,
            cleaned_text=cleaned_text,
            replaced_values=replaced_values,
            replaced_count=replaced_count,
        )
