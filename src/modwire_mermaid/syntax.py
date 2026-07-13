import json
from enum import StrEnum


class MermaidTextContext(StrEnum):
    COMMENT = "comment"
    LABEL = "label"
    STYLE = "style"
    TEXT = "text"
    TITLE = "title"
    URL = "url"


class MermaidSyntax:
    @staticmethod
    def require_single_line(
        value: str,
        context: MermaidTextContext = MermaidTextContext.TEXT,
        *,
        allow_empty: bool = False,
    ) -> str:
        if any(character in value for character in "\r\n") or (not allow_empty and not value.strip()):
            qualifier = "possibly empty " if allow_empty else "non-blank "
            raise ValueError(f"Mermaid {context.value} must be a {qualifier}single line")
        return value

    @staticmethod
    def quote(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)

    @staticmethod
    def raw(value: object) -> str:
        text = MermaidSyntax.require_single_line(str(value), MermaidTextContext.TEXT, allow_empty=True)
        replacements = {
            "&": "&amp;",
            ";": "&#59;",
            "[": "&#91;",
            "]": "&#93;",
            "{": "&#123;",
            "}": "&#125;",
        }
        return "".join(replacements.get(character, character) for character in text)

    @staticmethod
    def comment(value: object) -> str:
        return MermaidSyntax.require_single_line(str(value), MermaidTextContext.COMMENT)

    @staticmethod
    def style(value: object) -> str:
        text = MermaidSyntax.require_single_line(str(value), MermaidTextContext.STYLE)
        if ";" in text:
            raise ValueError("Mermaid style cannot contain statement separators")
        return text

    @classmethod
    def markdown(cls, value: str) -> str:
        quoted = cls.quote(value)
        return f'"`{quoted[1:-1]}`"'
