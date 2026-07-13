from ..compiler import DiagramCompiler
from ..source import MermaidWriter
from ..syntax import MermaidSyntax
from .diagram import ModwireFileTree, ModwireFileTreeIconMapping, ModwireFileTreeNode


class ModwireFileTreeCompiler(DiagramCompiler[ModwireFileTree]):
    @property
    def diagram_type(self) -> type[ModwireFileTree]:
        return ModwireFileTree

    def compile(self, diagram: ModwireFileTree) -> str:
        source = MermaidWriter(indentation="  ")
        source.lines(("---", "config:"), depth=0)
        source.line("treeView:", depth=1)
        source.lines(
            (
                f"rowIndent: {diagram.row_indent}",
                f"paddingX: {diagram.padding_x}",
                f"paddingY: {diagram.padding_y}",
                f"lineThickness: {diagram.line_thickness}",
                f"showIcons: {str(diagram.show_icons).lower()}",
                f"defaultIconPack: {MermaidSyntax.quote(diagram.default_icon_pack)}",
            ),
            depth=2,
        )
        self._mapping("filenameIcons", diagram.filename_icons, source)
        self._mapping("extensionIcons", diagram.extension_icons, source)
        source.line("themeVariables:", depth=1)
        source.line("treeView:", depth=2)
        source.lines(
            (
                f"labelFontSize: {MermaidSyntax.quote(diagram.label_font_size)}",
                f"labelColor: {MermaidSyntax.quote(diagram.label_color)}",
                f"lineColor: {MermaidSyntax.quote(diagram.line_color)}",
                f"iconColor: {MermaidSyntax.quote(diagram.icon_color)}",
                f"descriptionColor: {MermaidSyntax.quote(diagram.description_color)}",
                f"highlightBg: {MermaidSyntax.quote(diagram.highlight_background)}",
                f"highlightStroke: {MermaidSyntax.quote(diagram.highlight_stroke)}",
            ),
            depth=3,
        )
        source.lines(("---", "treeView-beta"), depth=0)
        source.lines((f"%% {MermaidSyntax.comment(comment)}" for comment in diagram.comments), depth=2)
        self._node(diagram.root, depth=1, source=source)
        return source.render()

    def _node(self, node: ModwireFileTreeNode, depth: int, source: MermaidWriter) -> None:
        label = MermaidSyntax.quote(node.label) + ("/" if node.is_directory else "")
        annotations: list[str] = []
        if node.icon:
            annotations.append(f"icon({node.icon})")
        if node.css_classes:
            annotations.append(f":::{' '.join(node.css_classes)}")
        if node.description:
            annotations.append(f"## {MermaidSyntax.raw(node.description)}")
        suffix = " " + " ".join(annotations) if annotations else ""
        source.line(f"{label}{suffix}", depth=depth * 2)
        for child in node.children:
            self._node(child, depth=depth + 1, source=source)

    def _mapping(
        self,
        name: str,
        values: tuple[ModwireFileTreeIconMapping, ...],
        source: MermaidWriter,
    ) -> None:
        source.line(f"{name}:", depth=2)
        source.lines(
            (f"{MermaidSyntax.quote(item.pattern)}: {MermaidSyntax.quote(item.icon)}" for item in values), depth=3
        )
