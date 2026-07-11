from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from ..contracts import (
    ModwireBaseDiagram,
    ModwireDiagramContract,
    ModwireDiagramError,
    ModwireDiagramIdentifier,
    ModwireSyntaxFeature,
)


class ModwireFlowchartDirection(StrEnum):
    TOP_DOWN = "TD"
    TOP_BOTTOM = "TB"
    BOTTOM_TOP = "BT"
    RIGHT_LEFT = "RL"
    LEFT_RIGHT = "LR"


class ModwireFlowchartShape(StrEnum):
    BANG = "bang"
    CARD = "notch-rect"
    CLOUD = "cloud"
    COLLATE = "hourglass"
    COMMUNICATION_LINK = "bolt"
    COMMENT = "brace"
    COMMENT_RIGHT = "brace-r"
    COMMENTS = "braces"
    DATA_INPUT = "lean-r"
    DATA_OUTPUT = "lean-l"
    DATA_STORE = "datastore"
    DATABASE = "cyl"
    DECISION = "diam"
    DELAY = "delay"
    DIRECT_ACCESS_STORAGE = "h-cyl"
    DISK_STORAGE = "lin-cyl"
    DISPLAY = "curv-trap"
    DIVIDED_PROCESS = "div-rect"
    DOCUMENT = "doc"
    EVENT = "rounded"
    EXTRACT = "tri"
    FORK_JOIN = "fork"
    INTERNAL_STORAGE = "win-pane"
    JUNCTION = "f-circ"
    LINED_DOCUMENT = "lin-doc"
    LINED_PROCESS = "lin-rect"
    LOOP_LIMIT = "notch-pent"
    MANUAL_FILE = "flip-tri"
    MANUAL_INPUT = "sl-rect"
    MANUAL_OPERATION = "trap-t"
    MULTI_DOCUMENT = "docs"
    MULTI_PROCESS = "st-rect"
    ODD = "odd"
    PAPER_TAPE = "flag"
    PREPARE = "hex"
    PRIORITY_ACTION = "trap-b"
    PROCESS = "rect"
    START = "circle"
    SMALL_START = "sm-circ"
    STOP = "dbl-circ"
    FRAMED_STOP = "fr-circ"
    STORED_DATA = "bow-rect"
    SUBPROCESS = "fr-rect"
    SUMMARY = "cross-circ"
    TAGGED_DOCUMENT = "tag-doc"
    TAGGED_PROCESS = "tag-rect"
    TERMINAL = "stadium"
    TEXT = "text"


class ModwireFlowchartTextFormat(StrEnum):
    PLAIN = "plain"
    MARKDOWN = "markdown"


class ModwireFlowchartNode(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    label: str
    shape: ModwireFlowchartShape
    text_format: ModwireFlowchartTextFormat
    css_classes: tuple[str, ...]

    @model_validator(mode="after")
    def validate_node(self):
        if self.id == "end":
            raise ModwireDiagramError("Lowercase 'end' is reserved by the Mermaid flowchart parser")
        return self


class ModwireFlowchartIconForm(StrEnum):
    NONE = ""
    SQUARE = "square"
    CIRCLE = "circle"
    ROUNDED = "rounded"


class ModwireFlowchartLabelPosition(StrEnum):
    TOP = "t"
    BOTTOM = "b"


class ModwireFlowchartIconNode(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    icon: str
    form: ModwireFlowchartIconForm
    label: str
    position: ModwireFlowchartLabelPosition
    height: int = Field(ge=48)
    css_classes: tuple[str, ...]

    @model_validator(mode="after")
    def validate_node(self):
        if self.id == "end":
            raise ModwireDiagramError("Lowercase 'end' is reserved by the Mermaid flowchart parser")
        return self


class ModwireFlowchartImageConstraint(StrEnum):
    ON = "on"
    OFF = "off"


class ModwireFlowchartImageNode(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    image_url: str
    label: str
    position: ModwireFlowchartLabelPosition
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    constraint: ModwireFlowchartImageConstraint
    css_classes: tuple[str, ...]

    @model_validator(mode="after")
    def validate_node(self):
        if self.id == "end":
            raise ModwireDiagramError("Lowercase 'end' is reserved by the Mermaid flowchart parser")
        return self


ModwireFlowchartNodeType = ModwireFlowchartNode | ModwireFlowchartIconNode | ModwireFlowchartImageNode


class ModwireFlowchartEdgeLine(StrEnum):
    NORMAL = "normal"
    THICK = "thick"
    DOTTED = "dotted"
    INVISIBLE = "invisible"


class ModwireFlowchartEdgeEnd(StrEnum):
    NONE = ""
    ARROW = ">"
    CIRCLE = "o"
    CROSS = "x"


class ModwireFlowchartAnimation(StrEnum):
    NONE = ""
    FAST = "fast"
    SLOW = "slow"


class ModwireFlowchartCurve(StrEnum):
    DEFAULT = ""
    BASIS = "basis"
    BUMP_X = "bumpX"
    BUMP_Y = "bumpY"
    CARDINAL = "cardinal"
    CATMULL_ROM = "catmullRom"
    LINEAR = "linear"
    MONOTONE_X = "monotoneX"
    MONOTONE_Y = "monotoneY"
    NATURAL = "natural"
    STEP = "step"
    STEP_AFTER = "stepAfter"
    STEP_BEFORE = "stepBefore"


class ModwireFlowchartEdge(ModwireDiagramContract):
    id: str
    source: ModwireDiagramIdentifier
    target: ModwireDiagramIdentifier
    label: str
    text_format: ModwireFlowchartTextFormat
    line: ModwireFlowchartEdgeLine
    source_end: ModwireFlowchartEdgeEnd
    target_end: ModwireFlowchartEdgeEnd
    minimum_length: int = Field(ge=1)
    animation: ModwireFlowchartAnimation
    curve: ModwireFlowchartCurve
    css_classes: tuple[str, ...]

    @model_validator(mode="after")
    def validate_edge(self):
        if self.id and not self.id.replace("_", "a").isalnum():
            raise ModwireDiagramError("Flowchart edge IDs must be alphanumeric or underscores")
        if self.line is ModwireFlowchartEdgeLine.INVISIBLE and (
            self.source_end is not ModwireFlowchartEdgeEnd.NONE
            or self.target_end is not ModwireFlowchartEdgeEnd.NONE
            or self.label
        ):
            raise ModwireDiagramError("Invisible edges cannot have ends or labels")
        if (
            self.animation is not ModwireFlowchartAnimation.NONE or self.curve is not ModwireFlowchartCurve.DEFAULT
        ) and not self.id:
            raise ModwireDiagramError("Animated or curved edges require an ID")
        return self


class ModwireFlowchartSubgraph(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    label: str
    direction: ModwireFlowchartDirection
    node_ids: tuple[ModwireDiagramIdentifier, ...]
    children: tuple[ModwireFlowchartSubgraph, ...]


class ModwireFlowchartInteractionKind(StrEnum):
    LINK = "link"
    CALLBACK = "callback"


class ModwireFlowchartLinkTarget(StrEnum):
    SELF = "_self"
    BLANK = "_blank"
    PARENT = "_parent"
    TOP = "_top"


class ModwireFlowchartInteraction(ModwireDiagramContract):
    node_id: ModwireDiagramIdentifier
    kind: ModwireFlowchartInteractionKind
    reference: str
    tooltip: str
    link_target: ModwireFlowchartLinkTarget


class ModwireFlowchartStyleProperty(ModwireDiagramContract):
    name: str
    value: str

    def mermaid(self) -> str:
        return f"{self.name}:{self.value}"


class ModwireFlowchartNodeStyle(ModwireDiagramContract):
    node_id: ModwireDiagramIdentifier
    properties: tuple[ModwireFlowchartStyleProperty, ...]


class ModwireFlowchartLinkStyle(ModwireDiagramContract):
    edge_indexes: tuple[int, ...]
    use_default: bool
    properties: tuple[ModwireFlowchartStyleProperty, ...]


class ModwireFlowchartStyleDefinition(ModwireDiagramContract):
    names: tuple[str, ...]
    properties: tuple[ModwireFlowchartStyleProperty, ...]


class ModwireFlowchart(ModwireBaseDiagram):
    docs_url = "https://mermaid.js.org/syntax/flowchart.html"
    syntax_features = (
        ModwireSyntaxFeature("comments", "test_flowchart_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("direction", "test_flowchart_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("interaction", "test_flowchart_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("links-between-nodes", "test_flowchart_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("node-shapes", "test_flowchart_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("special-shapes-in-mermaid-flowcharts-v1130", "test_flowchart_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("styling-and-classes", "test_flowchart_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("subgraphs", "test_flowchart_covers_rich_mermaid_syntax"),
    )

    nodes: tuple[ModwireFlowchartNodeType, ...]
    edges: tuple[ModwireFlowchartEdge, ...]
    subgraphs: tuple[ModwireFlowchartSubgraph, ...]
    direction: ModwireFlowchartDirection
    interactions: tuple[ModwireFlowchartInteraction, ...]
    node_styles: tuple[ModwireFlowchartNodeStyle, ...]
    link_styles: tuple[ModwireFlowchartLinkStyle, ...]
    style_definitions: tuple[ModwireFlowchartStyleDefinition, ...]
    comments: tuple[str, ...]
    markdown_auto_wrap: bool
    default_curve: ModwireFlowchartCurve

    @model_validator(mode="after")
    def validate_graph(self):
        identifiers = tuple(node.id for node in self.nodes)
        self._require_children(self.nodes, "Flowchart")
        self._validate_unique_children(identifiers, "Flowchart node")
        subgraph_ids = self._subgraph_ids(self.subgraphs)
        self._validate_unique_children(subgraph_ids, "Flowchart subgraph")
        endpoints = set(identifiers) | set(subgraph_ids)
        self._validate_child_references(
            endpoints,
            (value for edge in self.edges for value in (edge.source, edge.target)),
            "Flowchart edge",
        )
        self._validate_child_references(
            identifiers, (item.node_id for item in self.interactions), "Flowchart interaction"
        )
        self._validate_child_references(
            identifiers, (item.node_id for item in self.node_styles), "Flowchart node style"
        )
        edge_ids = tuple(edge.id for edge in self.edges if edge.id)
        self._validate_unique_children(edge_ids, "Flowchart edge ID")
        for subgraph in self.subgraphs:
            self._validate_subgraph(subgraph, set(identifiers))
        return self

    def _subgraph_ids(self, values: tuple[ModwireFlowchartSubgraph, ...]) -> tuple[ModwireDiagramIdentifier, ...]:
        return tuple(item.id for item in values) + tuple(
            value for item in values for value in self._subgraph_ids(item.children)
        )

    def _validate_subgraph(self, subgraph: ModwireFlowchartSubgraph, identifiers: set[str]) -> None:
        self._validate_child_references(identifiers, subgraph.node_ids, f"Flowchart subgraph {subgraph.id}")
        for child in subgraph.children:
            self._validate_subgraph(child, identifiers)
