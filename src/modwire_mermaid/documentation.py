from html.parser import HTMLParser


class MermaidDocumentationOutlineParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._in_outline = False
        self._in_outline_link = False
        self._heading_depth = 0
        self._outline_text: list[str] = []
        self._heading_text: list[str] = []
        self._outline: list[str] = []
        self._headings: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "nav" and attributes.get("aria-labelledby") == "doc-outline-aria-label":
            self._in_outline = True
        elif self._in_outline and tag == "a" and (attributes.get("href") or "").startswith("#"):
            self._in_outline_link = True
            self._outline_text = []
        if tag in {"h2", "h3"} and attributes.get("id"):
            self._heading_depth += 1
            self._heading_text = []

    def handle_endtag(self, tag: str) -> None:
        if self._in_outline_link and tag == "a":
            self._append(self._outline, self._outline_text)
            self._in_outline_link = False
        if self._in_outline and tag == "nav":
            self._in_outline = False
        if self._heading_depth and tag in {"h2", "h3"}:
            self._append(self._headings, self._heading_text)
            self._heading_depth = 0

    def handle_data(self, data: str) -> None:
        if self._in_outline_link:
            self._outline_text.append(data)
        if self._heading_depth:
            self._heading_text.append(data)

    def sections(self) -> tuple[str, ...]:
        return tuple(self._outline or self._headings)

    @staticmethod
    def slug(value: str) -> str:
        words = "-".join(value.strip().lower().split())
        return "".join(character for character in words if character.isalnum() or character == "-").strip("-")

    @classmethod
    def extract(cls, html: str) -> tuple[str, ...]:
        parser = cls()
        parser.feed(html)
        return parser.sections()

    @staticmethod
    def _append(target: list[str], fragments: list[str]) -> None:
        value = " ".join("".join(fragments).split())
        if value and value not in target:
            target.append(value)
