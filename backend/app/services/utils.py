from typing import Tuple


class TextUtils:
    @staticmethod
    def return_placeholder_with_counter(
        text: str, pattern, placeholder: str
    ) -> Tuple[str, dict[str, str]]:
        """Utility to replace matches and number the placeholders."""

        replaced_values: dict[str, str] = {}
        count = 0

        def replace_with_counter(match):
            nonlocal count
            count += 1
            placeholder_with_counter = f"[{placeholder}_{count}]"
            replaced_values[f"{placeholder}_{count}"] = match.group(0)
            return placeholder_with_counter

        text = pattern.sub(replace_with_counter, text)

        return text, replaced_values
