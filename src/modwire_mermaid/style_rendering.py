from .syntax import MermaidSyntax


class MermaidStyleRendering:
    @staticmethod
    def property(name: str, value: str) -> str:
        return f"{MermaidSyntax.style(name)}:{MermaidSyntax.style(value)}"
