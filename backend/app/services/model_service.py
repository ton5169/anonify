from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from app.core.config import HF_TOKEN
from app.services.base import CleanedTextResult, PiiRule, RuleResult
from app.services.utils import TextUtils
from transformers import pipeline


class BaseModelRule(PiiRule, ABC):
    _pii_ner: Callable[[str], list[dict[str, Any]]]

    @property
    @abstractmethod
    def placeholder(self) -> str: ...

    def _apply_rule_and_get_replaced_values(
        self, text: str, entities: list[dict[str, Any]], method: str
    ) -> RuleResult:
        text, replaced_count, replaced_values = (
            TextUtils.redact_entities_with_counter(text, entities, method)
        )
        return RuleResult(text, replaced_values, replaced_count)

    def extract_entities(self, text: str) -> list[dict[str, Any]]:
        entities = self._pii_ner(text)
        return TextUtils.normalize_entity_labels(entities)

    def apply(self, text: str, method: str) -> str:
        return self._apply_rule_and_get_replaced_values(
            text, self.extract_entities(text), method
        ).text

    def replaced_values(self, text: str, method: str) -> dict[str, str]:
        return self._apply_rule_and_get_replaced_values(
            text, self.extract_entities(text), method
        ).replaced_values

    def replaced_count(self, text: str, method: str) -> dict[str, int]:
        return self._apply_rule_and_get_replaced_values(
            text, self.extract_entities(text), method
        ).replaced_count


class ModelRuleAbAi(BaseModelRule):
    def __init__(self):
        self._pii_ner = pipeline(
            task='token-classification',
            model='ab-ai/pii_model',
            tokenizer='ab-ai/pii_model',
            token=HF_TOKEN,
            aggregation_strategy='simple',
        )

    @property
    def placeholder(self) -> str:
        return 'model/ab-ai'


class ModelRuleBertBase(BaseModelRule):
    def __init__(self):
        self._pii_ner = pipeline(
            task='token-classification',
            model='dslim/bert-base-NER',
            tokenizer='dslim/bert-base-NER',
            token=HF_TOKEN,
            aggregation_strategy='max',
        )

    @property
    def placeholder(self) -> str:
        return 'model/bert-base-NER'


class RemovalServiceModel:
    def __init__(self, rules: list[PiiRule]) -> None:
        self._rules = rules
        self._method = 'model'

    def _apply_rules(self, text: str) -> tuple[str, str]:
        cleaned_text = text
        for rule in self._rules:
            cleaned_text = rule.apply(cleaned_text, rule.placeholder)

        return cleaned_text, self._method

    def replaced_values(self, text: str) -> dict[str, str]:
        all_replaced_values: dict[str, str] = {}
        for rule in self._rules:
            replaced_values = rule.replaced_values(text, rule.placeholder)
            all_replaced_values.update(replaced_values)

        return all_replaced_values

    def replaced_count(self, text: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for rule in self._rules:
            replaced_count = rule.replaced_count(text, rule.placeholder)
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
