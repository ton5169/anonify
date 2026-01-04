from collections import defaultdict
from typing import Any, Dict, List, Tuple


class TextUtils:
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

        return text, replaced_count, replaced_values

    @staticmethod
    def redact_entities_with_counter(
        text: str,
        entities: List[Dict[str, Any]],
        *,
        label_key: str = "entity_group",
        start_at: int = 1,
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

        # 1) Sort left-to-right, prefer longer spans if same start
        ents = sorted(entities, key=lambda e: (e["start"], -(e["end"] - e["start"])))

        # 2) Remove overlaps deterministically
        filtered = []
        last_end = -1
        for e in ents:
            if e["start"] < last_end:
                continue
            filtered.append(e)
            last_end = e["end"]

        # 3) Assign numbered placeholders
        next_idx = defaultdict(lambda: start_at)
        assigned = []
        mapping: Dict[str, str] = {}

        for e in filtered:
            label = e[label_key]
            idx = next_idx[label]
            next_idx[label] += 1

            placeholder_key = f"{label}_{idx}"  # EMAIL_1
            placeholder = f"[{placeholder_key}]"  # [EMAIL_1]

            assigned.append((e["start"], e["end"], placeholder))
            mapping[placeholder_key] = text[e["start"] : e["end"]]

        # 4) Replace spans right-to-left to preserve offsets
        redacted = text
        for start, end, placeholder in sorted(assigned, reverse=True):
            redacted = redacted[:start] + placeholder + redacted[end:]

        # 5) Build counters
        counters = {label: next_idx[label] - start_at for label in next_idx}

        return redacted, counters, mapping
