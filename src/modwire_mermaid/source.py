from collections.abc import Iterable


class MermaidWriter:
    """Build deterministic LF-only Mermaid source one safe line at a time."""

    def __init__(self, indentation: str = "  "):
        if not indentation or any(character in indentation for character in "\r\n"):
            raise ValueError("Mermaid writer indentation must be non-empty and single-line")
        self._indentation = indentation
        self._lines: list[str] = []

    def line(self, value: str, depth: int = 0) -> None:
        if depth < 0:
            raise ValueError("Mermaid writer depth cannot be negative")
        if any(character in value for character in "\r\n"):
            raise ValueError("Mermaid writer lines cannot contain line breaks")
        self._lines.append(f"{self._indentation * depth}{value}".rstrip())

    def lines(self, values: Iterable[str], depth: int = 0) -> None:
        for value in values:
            self.line(value, depth)

    def block(self, value: str) -> None:
        """Append rendered text after canonical newline normalization."""
        normalized = value.replace("\r\n", "\n").replace("\r", "\n")
        for line in normalized.rstrip("\n").split("\n"):
            self.line(line)

    def render(self) -> str:
        return "\n".join(self._lines).rstrip("\n") + "\n"
