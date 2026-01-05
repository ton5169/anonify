from collections import defaultdict
import string
from typing import Any, Dict, List, Tuple


class TextUtils:
    # Label normalization mapping for model entities
    _LABEL_NORMALIZATION: Dict[str, str] = {
        "PER": "PERSON",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        "MISC": "MISCELLANEOUS",
    }

    @staticmethod
    def namespace_dict(d: Dict[str, Any], method: str) -> Dict[str, Any]:
        """Namespace dictionary keys with method prefix."""
        return {f"{method}:{k}": v for k, v in d.items()}

    @staticmethod
    def normalize_entity_labels(entities: List[Dict[str, Any]], label_key: str = "entity_group") -> List[Dict[str, Any]]:
        """Normalize entity labels according to the normalization mapping."""
        normalized = []
        for entity in entities:
            entity = entity.copy()
            if label_key in entity:
                label = entity[label_key]
                if label in TextUtils._LABEL_NORMALIZATION:
                    entity[label_key] = TextUtils._LABEL_NORMALIZATION[label]
            normalized.append(entity)
        return normalized

    @staticmethod
    def _trim_span(text: str, start: int, end: int) -> Tuple[int, int]:
        """
        Trim leading/trailing whitespace and trailing/leading punctuation from a span.
        Keeps offsets consistent with the original string.
        """
        # First trim whitespace
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1

        # Then trim punctuation (common for NER/PII models)
        punct = set(string.punctuation)
        while start < end and text[start] in punct:
            start += 1
        while end > start and text[end - 1] in punct:
            end -= 1

        return start, end

    @staticmethod
    def return_placeholder_with_counter(
        text: str, method: str, pattern, placeholder: str
    ) -> Tuple[str, dict[str, int], dict[str, str]]:
        """Replace regex matches with numbered placeholders and collect originals."""

        replaced_values: dict[str, str] = {}
        count = 0

        def replace_with_counter(match):
            nonlocal count
            count += 1
            placeholder_with_counter = f"[{placeholder}_{count}]"
            # Store originals keyed by placeholder name; the caller can namespace.
            replaced_values[f"{placeholder}_{count}"] = match.group(0)
            return placeholder_with_counter

        text = pattern.sub(replace_with_counter, text)
        replaced_count = {placeholder: count} if count > 0 else {}

        # Namespace keys with method prefix
        namespaced_count = TextUtils.namespace_dict(replaced_count, method)
        namespaced_values = TextUtils.namespace_dict(replaced_values, method)

        return text, namespaced_count, namespaced_values

    @staticmethod
    def redact_entities_with_counter(
        text: str,
        entities: List[Dict[str, Any]],
        method: str,
        *,
        label_key: str = "entity_group",
        start_at: int = 1,
        trim_spans: bool = True,
    ) -> Tuple[str, Dict[str, int], Dict[str, str]]:
        """
        Replace entity spans with numbered placeholders per label, e.g. [EMAIL_1].

        Returns:
          redacted_text: str
          counters: dict[label -> count]
          mapping: dict[PLACEHOLDER -> original_text]

        Required entity fields:
          - start (int), end (int)
          - entity_group (or label_key)
        """

        # 1) Normalize, validate, and (optionally) trim spans
        normalized = []
        for e in entities:
            if "start" not in e or "end" not in e or label_key not in e:
                continue

            start = int(e["start"])
            end = int(e["end"])
            if start < 0 or end > len(text) or start >= end:
                continue

            if trim_spans:
                start, end = TextUtils._trim_span(text, start, end)
                if start >= end:
                    continue

            normalized.append({**e, "start": start, "end": end})

        # 2) Sort left-to-right, prefer longer spans if same start
        ents = sorted(normalized, key=lambda e: (e["start"], -(e["end"] - e["start"])))

        # 3) Remove overlaps deterministically
        filtered = []
        last_end = -1
        for e in ents:
            if e["start"] < last_end:
                continue
            filtered.append(e)
            last_end = e["end"]

        # 4) Assign numbered placeholders (numbering follows reading order)
        next_idx = defaultdict(lambda: start_at)
        assigned = []
        mapping: Dict[str, str] = {}

        for e in filtered:
            label = str(e[label_key])
            idx = next_idx[label]
            next_idx[label] += 1

            placeholder_key = f"{label}_{idx}"  # EMAIL_1
            placeholder = f"[{placeholder_key}]"  # [EMAIL_1]

            start, end = e["start"], e["end"]
            assigned.append((start, end, placeholder))
            mapping[placeholder_key] = text[start:end]  # use true substring

        # 5) Replace spans right-to-left to preserve offsets
        redacted = text
        for start, end, placeholder in sorted(
            assigned, key=lambda x: x[0], reverse=True
        ):
            redacted = redacted[:start] + placeholder + redacted[end:]

        # 6) Build counters
        counters = {label: next_idx[label] - start_at for label in next_idx}

        # 7) Namespace keys with method prefix
        namespaced_counters = TextUtils.namespace_dict(counters, method)
        namespaced_mapping = TextUtils.namespace_dict(mapping, method)

        return redacted, namespaced_counters, namespaced_mapping
