from collections.abc import Iterable


class MermaidSource:
    def __init__(self, indentation: str):
        if not indentation:
            raise ValueError("Mermaid source indentation cannot be empty")
        self._indentation = indentation
        self._lines: list[str] = []

    def line(self, value: str, depth: int) -> None:
        if depth < 0:
            raise ValueError("Mermaid source depth cannot be negative")
        if any(character in value for character in "\r\n"):
            raise ValueError("Mermaid source lines cannot contain line breaks")
        self._lines.append(f"{self._indentation * depth}{value}")

    def lines(self, values: Iterable[str], depth: int) -> None:
        for value in values:
            self.line(value, depth)

    def render(self) -> str:
        return "\n".join(self._lines) + "\n"
