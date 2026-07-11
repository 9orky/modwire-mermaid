import json


class MermaidSyntax:
    @staticmethod
    def require_single_line(value: str) -> str:
        if not value.strip() or any(character in value for character in "\r\n"):
            raise ValueError("Mermaid text must be a non-blank single line")
        return value

    @staticmethod
    def quote(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)

    @classmethod
    def markdown(cls, value: str) -> str:
        quoted = cls.quote(value)
        return f'"`{quoted[1:-1]}`"'
