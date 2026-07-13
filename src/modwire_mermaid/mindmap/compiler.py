from ..compiler import DiagramCompiler
from ..source import MermaidWriter
from ..syntax import MermaidSyntax
from .diagram import (
    ModwireMindmap,
    ModwireMindmapNode,
    ModwireMindmapShape,
    ModwireMindmapTextFormat,
)


class ModwireMindmapCompiler(DiagramCompiler[ModwireMindmap]):
    @property
    def diagram_type(self) -> type[ModwireMindmap]:
        return ModwireMindmap

    def compile(self, diagram: ModwireMindmap) -> str:
        source = MermaidWriter(indentation="  ")
        if diagram.layout.value:
            source.lines(("---", "config:"), depth=0)
            source.line(f"layout: {diagram.layout.value}", depth=1)
            source.line("---", depth=0)
        source.line("mindmap", depth=0)
        self._node(diagram.root, depth=1, source=source)
        return source.render()

    def _node(self, node: ModwireMindmapNode, depth: int, source: MermaidWriter) -> None:
        source.line(self._declaration(node), depth=depth)
        if node.icon_classes:
            source.line(f"::icon({' '.join(node.icon_classes)})", depth=depth)
        if node.css_classes:
            source.line(f":::{' '.join(node.css_classes)}", depth=depth)
        for child in node.children:
            self._node(child, depth=depth + 1, source=source)

    def _declaration(self, node: ModwireMindmapNode) -> str:
        if node.shape is ModwireMindmapShape.DEFAULT:
            return node.id
        label = self._label(node.label, node.text_format)
        delimiters = {
            ModwireMindmapShape.SQUARE: ("[", "]"),
            ModwireMindmapShape.ROUNDED_SQUARE: ("(", ")"),
            ModwireMindmapShape.CIRCLE: ("((", "))"),
            ModwireMindmapShape.BANG: ("))", "(("),
            ModwireMindmapShape.CLOUD: (")", "("),
            ModwireMindmapShape.HEXAGON: ("{{", "}}"),
        }
        opening, closing = delimiters[node.shape]
        return f"{node.id}{opening}{label}{closing}"

    @staticmethod
    def _label(value: str, text_format: ModwireMindmapTextFormat) -> str:
        escaped = MermaidSyntax.quote(value)
        if text_format is ModwireMindmapTextFormat.MARKDOWN:
            return f'"`{escaped[1:-1]}`"'
        return escaped
