from ..compiler import DiagramCompiler
from ..source import MermaidSource
from ..syntax import MermaidSyntax
from .diagram import (
    ModwireFlowchart,
    ModwireFlowchartInteractionKind,
    ModwireFlowchartSubgraph,
)
from .rendering import ModwireFlowchartRendering


class ModwireFlowchartCompiler(DiagramCompiler[ModwireFlowchart]):
    @property
    def diagram_type(self) -> type[ModwireFlowchart]:
        return ModwireFlowchart

    def compile(self, diagram: ModwireFlowchart) -> str:
        source = MermaidSource(indentation="  ")
        source.lines(("---", "config:"), depth=0)
        source.line(f"markdownAutoWrap: {str(diagram.markdown_auto_wrap).lower()}", depth=1)
        source.line("flowchart:", depth=1)
        source.line(f"curve: {diagram.default_curve.value or 'linear'}", depth=2)
        source.lines(("---", f"flowchart {diagram.direction.value}"), depth=0)
        source.lines((f"%% {comment}" for comment in diagram.comments), depth=2)
        grouped = {node_id for subgraph in diagram.subgraphs for node_id in self._nested_node_ids(subgraph)}
        source.lines(
            (ModwireFlowchartRendering.node(node) for node in diagram.nodes if node.id not in grouped), depth=2
        )
        for subgraph in diagram.subgraphs:
            self._subgraph(subgraph, diagram, depth=2, source=source)
        source.lines((ModwireFlowchartRendering.edge(edge) for edge in diagram.edges), depth=2)
        for edge in diagram.edges:
            properties = []
            if edge.animation.value:
                properties.extend(("animate: true", f"animation: {edge.animation.value}"))
            if edge.curve.value:
                properties.append(f"curve: {edge.curve.value}")
            if properties:
                source.line(f"{edge.id}@{{ {', '.join(properties)} }}", depth=2)
            if edge.css_classes:
                source.line(f"class {edge.id} {','.join(edge.css_classes)};", depth=2)
        for interaction in diagram.interactions:
            if interaction.kind is ModwireFlowchartInteractionKind.LINK:
                source.line(
                    f"click {interaction.node_id} href {MermaidSyntax.quote(interaction.reference)} "
                    f"{MermaidSyntax.quote(interaction.tooltip)} {interaction.link_target.value}",
                    depth=2,
                )
            else:
                tooltip = MermaidSyntax.quote(interaction.tooltip)
                source.line(
                    f"click {interaction.node_id} call {interaction.reference}() {tooltip}",
                    depth=2,
                )
        for style in diagram.node_styles:
            source.line(f"style {style.node_id} {self._properties(style.properties)}", depth=2)
        for style in diagram.link_styles:
            selector = "default" if style.use_default else ",".join(str(value) for value in style.edge_indexes)
            source.line(f"linkStyle {selector} {self._properties(style.properties)};", depth=2)
        for definition in diagram.style_definitions:
            source.line(f"classDef {','.join(definition.names)} {self._properties(definition.properties)};", depth=2)
        for node in diagram.nodes:
            if node.css_classes:
                source.line(f"class {node.id} {','.join(node.css_classes)};", depth=2)
        return source.render()

    def _subgraph(
        self,
        value: ModwireFlowchartSubgraph,
        diagram: ModwireFlowchart,
        depth: int,
        source: MermaidSource,
    ) -> None:
        source.line(f"subgraph {value.id}[{MermaidSyntax.quote(value.label)}]", depth=depth)
        source.line(f"direction {value.direction.value}", depth=depth + 2)
        nodes = {node.id: node for node in diagram.nodes}
        source.lines((ModwireFlowchartRendering.node(nodes[node_id]) for node_id in value.node_ids), depth=depth + 2)
        for child in value.children:
            self._subgraph(child, diagram, depth=depth + 2, source=source)
        source.line("end", depth=depth)

    def _nested_node_ids(self, value: ModwireFlowchartSubgraph) -> tuple[str, ...]:
        return value.node_ids + tuple(node_id for child in value.children for node_id in self._nested_node_ids(child))

    @staticmethod
    def _properties(values) -> str:
        return ",".join(value.mermaid() for value in values)
