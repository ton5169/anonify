from bs4 import BeautifulSoup


class HtmlService:
    def __init__(self):
        self._state = None

    def clean(self, html: str) -> str:
        text = BeautifulSoup(html, "html.parser").get_text()
        self._state = html
        return text

    def restore(self, text: str) -> str:
        if self._state is None:
            raise ValueError("No state available to restore HTML.")

        return self._state
