from __future__ import annotations

import re
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .contracts import (
    MODWIRE_CALLBACK_PATTERN,
    MODWIRE_URL_PATTERN,
    ModwireBaseDiagram,
    ModwireContractViolation,
    ModwireCssName,
    ModwireDiagramContract,
    ModwireDiagramIdentifier,
    ModwireDiagramReference,
    ModwireIconName,
    ModwireNonNegativeInt,
    ModwireOptionalText,
    ModwirePositiveInt,
    ModwireStyleName,
    ModwireStyleValue,
    ModwireSyntaxFeature,
    ModwireText,
    ModwireUrl,
    contract_validation_error,
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
    node_type: Literal["node"] = "node"
    id: ModwireDiagramIdentifier
    label: ModwireText
    shape: ModwireFlowchartShape = ModwireFlowchartShape.PROCESS
    text_format: ModwireFlowchartTextFormat = ModwireFlowchartTextFormat.PLAIN
    css_classes: tuple[ModwireCssName, ...] = ()

    @model_validator(mode="after")
    def validate_node(self):
        if self.id == "end":
            raise contract_validation_error(
                type(self).__name__,
                (ModwireContractViolation(("id",), "reserved_identifier", "Lowercase 'end' is reserved", self.id),),
            )
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
    node_type: Literal["icon"] = "icon"
    id: ModwireDiagramIdentifier
    icon: ModwireIconName
    form: ModwireFlowchartIconForm = ModwireFlowchartIconForm.NONE
    label: ModwireOptionalText = ""
    position: ModwireFlowchartLabelPosition = ModwireFlowchartLabelPosition.BOTTOM
    height: int = Field(default=48, ge=48)
    css_classes: tuple[ModwireCssName, ...] = ()

    @model_validator(mode="after")
    def validate_node(self):
        if self.id == "end":
            raise contract_validation_error(
                type(self).__name__,
                (ModwireContractViolation(("id",), "reserved_identifier", "Lowercase 'end' is reserved", self.id),),
            )
        return self


class ModwireFlowchartImageConstraint(StrEnum):
    ON = "on"
    OFF = "off"


class ModwireFlowchartImageNode(ModwireDiagramContract):
    node_type: Literal["image"] = "image"
    id: ModwireDiagramIdentifier
    image_url: ModwireUrl
    label: ModwireOptionalText = ""
    position: ModwireFlowchartLabelPosition = ModwireFlowchartLabelPosition.BOTTOM
    width: ModwirePositiveInt
    height: ModwirePositiveInt
    constraint: ModwireFlowchartImageConstraint = ModwireFlowchartImageConstraint.ON
    css_classes: tuple[ModwireCssName, ...] = ()

    @model_validator(mode="after")
    def validate_node(self):
        if self.id == "end":
            raise contract_validation_error(
                type(self).__name__,
                (ModwireContractViolation(("id",), "reserved_identifier", "Lowercase 'end' is reserved", self.id),),
            )
        return self


ModwireFlowchartNodeType = Annotated[
    ModwireFlowchartNode | ModwireFlowchartIconNode | ModwireFlowchartImageNode,
    Field(discriminator="node_type"),
]


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
    id: ModwireDiagramReference = ""
    source: ModwireDiagramIdentifier
    target: ModwireDiagramIdentifier
    label: ModwireOptionalText = ""
    text_format: ModwireFlowchartTextFormat = ModwireFlowchartTextFormat.PLAIN
    line: ModwireFlowchartEdgeLine = ModwireFlowchartEdgeLine.NORMAL
    source_end: ModwireFlowchartEdgeEnd = ModwireFlowchartEdgeEnd.NONE
    target_end: ModwireFlowchartEdgeEnd = ModwireFlowchartEdgeEnd.ARROW
    minimum_length: int = Field(default=1, ge=1)
    animation: ModwireFlowchartAnimation = ModwireFlowchartAnimation.NONE
    curve: ModwireFlowchartCurve = ModwireFlowchartCurve.DEFAULT
    css_classes: tuple[ModwireCssName, ...] = ()

    @model_validator(mode="after")
    def validate_edge(self):
        if self.id and not self.id.replace("_", "a").isalnum():
            raise contract_validation_error(
                type(self).__name__,
                (
                    ModwireContractViolation(
                        ("id",), "invalid_identifier", "Edge IDs must be alphanumeric or underscores", self.id
                    ),
                ),
            )
        if self.line is ModwireFlowchartEdgeLine.INVISIBLE and (
            self.source_end is not ModwireFlowchartEdgeEnd.NONE
            or self.target_end is not ModwireFlowchartEdgeEnd.NONE
            or self.label
        ):
            raise contract_validation_error(
                type(self).__name__,
                (
                    ModwireContractViolation(
                        ("line",),
                        "invalid_configuration",
                        "Invisible edges cannot have ends or labels",
                        self.line,
                    ),
                ),
            )
        if (
            self.animation is not ModwireFlowchartAnimation.NONE or self.curve is not ModwireFlowchartCurve.DEFAULT
        ) and not self.id:
            raise contract_validation_error(
                type(self).__name__,
                (
                    ModwireContractViolation(
                        ("id",), "invalid_configuration", "Animated or curved edges require an ID", self.id
                    ),
                ),
            )
        return self


class ModwireFlowchartSubgraph(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    label: ModwireOptionalText = ""
    direction: ModwireFlowchartDirection = ModwireFlowchartDirection.TOP_BOTTOM
    node_ids: tuple[ModwireDiagramIdentifier, ...] = ()
    children: tuple[ModwireFlowchartSubgraph, ...] = ()


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
    reference: ModwireText
    tooltip: ModwireOptionalText = ""
    link_target: ModwireFlowchartLinkTarget = ModwireFlowchartLinkTarget.SELF

    @model_validator(mode="after")
    def validate_reference(self):
        pattern = (
            MODWIRE_CALLBACK_PATTERN if self.kind is ModwireFlowchartInteractionKind.CALLBACK else MODWIRE_URL_PATTERN
        )
        if re.fullmatch(pattern, self.reference) is None:
            raise contract_validation_error(
                type(self).__name__,
                (
                    ModwireContractViolation(
                        ("reference",),
                        "invalid_interaction_reference",
                        "Interaction reference is invalid for its kind",
                        self.reference,
                    ),
                ),
            )
        return self


class ModwireFlowchartStyleProperty(ModwireDiagramContract):
    name: ModwireStyleName
    value: ModwireStyleValue


class ModwireFlowchartNodeStyle(ModwireDiagramContract):
    node_id: ModwireDiagramIdentifier
    properties: tuple[ModwireFlowchartStyleProperty, ...] = ()


class ModwireFlowchartLinkStyle(ModwireDiagramContract):
    edge_indexes: tuple[ModwireNonNegativeInt, ...] = ()
    use_default: bool = False
    properties: tuple[ModwireFlowchartStyleProperty, ...] = ()


class ModwireFlowchartStyleDefinition(ModwireDiagramContract):
    names: tuple[ModwireCssName, ...]
    properties: tuple[ModwireFlowchartStyleProperty, ...] = ()


class ModwireFlowchart(ModwireBaseDiagram):
    kind: Literal["flowchart"] = "flowchart"
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
    edges: tuple[ModwireFlowchartEdge, ...] = ()
    subgraphs: tuple[ModwireFlowchartSubgraph, ...] = ()
    direction: ModwireFlowchartDirection = ModwireFlowchartDirection.TOP_BOTTOM
    interactions: tuple[ModwireFlowchartInteraction, ...] = ()
    node_styles: tuple[ModwireFlowchartNodeStyle, ...] = ()
    link_styles: tuple[ModwireFlowchartLinkStyle, ...] = ()
    style_definitions: tuple[ModwireFlowchartStyleDefinition, ...] = ()
    comments: tuple[ModwireText, ...] = ()
    markdown_auto_wrap: bool = True
    default_curve: ModwireFlowchartCurve = ModwireFlowchartCurve.LINEAR

    @model_validator(mode="after")
    def validate_graph(self):
        identifiers = tuple(node.id for node in self.nodes)
        self._require_children(self.nodes, "Flowchart")
        self._validate_unique_children(identifiers, "Flowchart node")
        subgraph_ids = self._subgraph_ids(self.subgraphs)
        self._validate_unique_children(subgraph_ids, "Flowchart subgraph")
        collisions = set(identifiers) & set(subgraph_ids)
        if collisions:
            raise contract_validation_error(
                type(self).__name__,
                (
                    ModwireContractViolation(
                        ("subgraphs",),
                        "duplicate_identifier",
                        "Node and subgraph identifiers must not collide",
                        sorted(collisions),
                    ),
                ),
            )
        endpoints = set(identifiers) | set(subgraph_ids)
        self._validate_located_references(
            endpoints,
            (
                (location, reference)
                for index, edge in enumerate(self.edges)
                for location, reference in (
                    (("edges", index, "source"), edge.source),
                    (("edges", index, "target"), edge.target),
                )
            ),
            "Flowchart edge",
        )
        self._validate_located_references(
            identifiers,
            ((("interactions", index, "node_id"), item.node_id) for index, item in enumerate(self.interactions)),
            "Flowchart interaction",
        )
        self._validate_located_references(
            identifiers,
            ((("node_styles", index, "node_id"), item.node_id) for index, item in enumerate(self.node_styles)),
            "Flowchart node style",
        )
        edge_ids = tuple(edge.id for edge in self.edges if edge.id)
        self._validate_unique_children(edge_ids, "Flowchart edge ID")
        for index, subgraph in enumerate(self.subgraphs):
            self._validate_subgraph(subgraph, set(identifiers), ("subgraphs", index))
        grouped = tuple(node_id for subgraph in self.subgraphs for node_id in self._nested_node_ids(subgraph))
        self._validate_unique_children(grouped, "Flowchart subgraph ownership")
        for style_index, style in enumerate(self.link_styles):
            if style.use_default and style.edge_indexes:
                raise contract_validation_error(
                    type(self).__name__,
                    (
                        ModwireContractViolation(
                            ("link_styles", style_index, "edge_indexes"),
                            "invalid_configuration",
                            "Default link styles cannot also select edge indexes",
                            style.edge_indexes,
                        ),
                    ),
                )
            if not style.use_default and not style.edge_indexes:
                raise contract_validation_error(
                    type(self).__name__,
                    (
                        ModwireContractViolation(
                            ("link_styles", style_index, "edge_indexes"),
                            "invalid_configuration",
                            "Link styles require edge indexes or use_default=True",
                            style.edge_indexes,
                        ),
                    ),
                )
            violations = tuple(
                ModwireContractViolation(
                    ("link_styles", style_index, "edge_indexes", index_position),
                    "index_out_of_range",
                    "Edge index {index} is outside the diagram edge range",
                    edge_index,
                    {"index": edge_index},
                )
                for index_position, edge_index in enumerate(style.edge_indexes)
                if edge_index < 0 or edge_index >= len(self.edges)
            )
            if violations:
                raise contract_validation_error(type(self).__name__, violations)
        return self

    def _subgraph_ids(self, values: tuple[ModwireFlowchartSubgraph, ...]) -> tuple[ModwireDiagramIdentifier, ...]:
        return tuple(item.id for item in values) + tuple(
            value for item in values for value in self._subgraph_ids(item.children)
        )

    def _validate_subgraph(
        self, subgraph: ModwireFlowchartSubgraph, identifiers: set[str], path: tuple[str | int, ...]
    ) -> None:
        self._validate_located_references(
            identifiers,
            (((*path, "node_ids", index), node_id) for index, node_id in enumerate(subgraph.node_ids)),
            f"Flowchart subgraph {subgraph.id}",
        )
        for index, child in enumerate(subgraph.children):
            self._validate_subgraph(child, identifiers, (*path, "children", index))

    def _nested_node_ids(self, value: ModwireFlowchartSubgraph) -> tuple[str, ...]:
        return value.node_ids + tuple(node_id for child in value.children for node_id in self._nested_node_ids(child))
