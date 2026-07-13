from typing import Literal

from pydantic import model_validator

from ..contracts import (
    ModwireBaseDiagram,
    ModwireDiagramContract,
    ModwireDiagramDirection,
    ModwireDiagramIdentifier,
    ModwireSyntaxFeature,
)
from ..graph import (
    ModwireFlowchartEdge,
    ModwireFlowchartInteraction,
    ModwireFlowchartLinkStyle,
    ModwireFlowchartNodeStyle,
    ModwireFlowchartNodeType,
    ModwireFlowchartShape,
    ModwireFlowchartStyleDefinition,
)

ModwireSwimlaneNodeShape = ModwireFlowchartShape
ModwireSwimlaneNode = ModwireFlowchartNodeType
ModwireSwimlaneEdge = ModwireFlowchartEdge


class ModwireSwimlane(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    label: str
    nodes: tuple[ModwireFlowchartNodeType, ...]


class ModwireSwimlaneDiagram(ModwireBaseDiagram):
    kind: Literal["swimlane"] = "swimlane"
    docs_url = "https://mermaid.js.org/syntax/swimlanes.html"
    syntax_features = (
        ModwireSyntaxFeature("accessibility", "test_swimlane_reuses_full_flowchart_node_and_edge_rendering"),
        ModwireSyntaxFeature("edges", "test_swimlane_reuses_full_flowchart_node_and_edge_rendering"),
        ModwireSyntaxFeature("lanes", "test_swimlane_reuses_full_flowchart_node_and_edge_rendering"),
        ModwireSyntaxFeature("nodes", "test_swimlane_reuses_full_flowchart_node_and_edge_rendering"),
    )

    lanes: tuple[ModwireSwimlane, ...]
    edges: tuple[ModwireFlowchartEdge, ...] = ()
    direction: ModwireDiagramDirection = ModwireDiagramDirection.TOP_BOTTOM
    accessibility_title: str = ""
    accessibility_description: str = ""
    interactions: tuple[ModwireFlowchartInteraction, ...] = ()
    node_styles: tuple[ModwireFlowchartNodeStyle, ...] = ()
    link_styles: tuple[ModwireFlowchartLinkStyle, ...] = ()
    style_definitions: tuple[ModwireFlowchartStyleDefinition, ...] = ()
    comments: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_graph(self):
        self._require_children(self.lanes, "Swimlane diagram")
        self._validate_unique_children((lane.id for lane in self.lanes), "Swimlane diagram")
        nodes = tuple(node.id for lane in self.lanes for node in lane.nodes)
        self._validate_unique_children(nodes, "Swimlane diagram")
        self._validate_child_references(
            nodes,
            (value for edge in self.edges for value in (edge.source, edge.target)),
            "Swimlane edge",
        )
        self._validate_child_references(
            nodes,
            (interaction.node_id for interaction in self.interactions),
            "Swimlane interaction",
        )
        self._validate_child_references(
            nodes,
            (style.node_id for style in self.node_styles),
            "Swimlane style",
        )
        return self
