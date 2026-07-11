from ..syntax import MermaidSyntax
from .diagram import (
    ModwireFlowchartEdge,
    ModwireFlowchartEdgeEnd,
    ModwireFlowchartEdgeLine,
    ModwireFlowchartIconNode,
    ModwireFlowchartImageNode,
    ModwireFlowchartNode,
    ModwireFlowchartTextFormat,
)


class ModwireFlowchartRendering:
    @classmethod
    def node(cls, node) -> str:
        if isinstance(node, ModwireFlowchartNode):
            label = cls.label(node.label, node.text_format)
            return f"{node.id}@{{ shape: {node.shape.value}, label: {label} }}"
        if isinstance(node, ModwireFlowchartIconNode):
            values = [
                f'icon: "{node.icon}"',
                f"label: {MermaidSyntax.quote(node.label)}",
                f'pos: "{node.position.value}"',
                f"h: {node.height}",
            ]
            if node.form.value:
                values.append(f'form: "{node.form.value}"')
            return f"{node.id}@{{ {', '.join(values)} }}"
        if not isinstance(node, ModwireFlowchartImageNode):
            raise TypeError(f"Unsupported flowchart node: {type(node).__name__}")
        image_url = MermaidSyntax.quote(node.image_url)
        label = MermaidSyntax.quote(node.label)
        values = (
            f'img: {image_url}, label: {label}, pos: "{node.position.value}", '
            f'w: {node.width}, h: {node.height}, constraint: "{node.constraint.value}"'
        )
        return f"{node.id}@{{ {values} }}"

    @classmethod
    def edge(cls, edge: ModwireFlowchartEdge) -> str:
        prefix = f"{edge.id}@" if edge.id else ""
        if edge.line is ModwireFlowchartEdgeLine.INVISIBLE:
            arrow = "~" * (edge.minimum_length + 2)
        elif edge.line is ModwireFlowchartEdgeLine.DOTTED:
            arrow = "-" + "." * edge.minimum_length + "-"
        else:
            character = "=" if edge.line is ModwireFlowchartEdgeLine.THICK else "-"
            arrow = character * (edge.minimum_length + 1)
        arrow = cls.source_end(edge.source_end) + arrow + edge.target_end.value
        label = f"|{cls.label(edge.label, edge.text_format)}|" if edge.label else ""
        return f"{edge.source} {prefix}{arrow}{label} {edge.target}"

    @staticmethod
    def source_end(value: ModwireFlowchartEdgeEnd) -> str:
        return "<" if value is ModwireFlowchartEdgeEnd.ARROW else value.value

    @staticmethod
    def label(value: str, text_format: ModwireFlowchartTextFormat) -> str:
        if text_format is ModwireFlowchartTextFormat.MARKDOWN:
            return MermaidSyntax.markdown(value)
        return MermaidSyntax.quote(value)
