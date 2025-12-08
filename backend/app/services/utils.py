import re


def return_placeholder_with_counter(text: str, pattern, placeholder: str) -> str:
    """Utility to replace matches and number the placeholders."""

    def replace_with_counter(match):
        nonlocal count
        count += 1
        return f"[{placeholder}_{count}]"

    temp_placeholder = f"__TEMP__{placeholder}__"
    text, n = pattern.subn(temp_placeholder, text)

    count = 0
    if n > 0:
        text = re.sub(re.escape(temp_placeholder), replace_with_counter, text)

    return text
