from typing import Tuple


class TextUtils:
    @staticmethod
    def return_placeholder_with_counter(
        text: str, method: str, pattern, placeholder: str
    ) -> Tuple[str, dict[str, str]]:
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

        return text, replaced_values
