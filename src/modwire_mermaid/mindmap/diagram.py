from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import model_validator

from ..contracts import (
    ModwireBaseDiagram,
    ModwireContractViolation,
    ModwireCssName,
    ModwireDiagramContract,
    ModwireDiagramIdentifier,
    ModwireMultilineText,
    ModwireSyntaxFeature,
    contract_validation_error,
)


class ModwireMindmapShape(StrEnum):
    DEFAULT = "default"
    SQUARE = "square"
    ROUNDED_SQUARE = "rounded-square"
    CIRCLE = "circle"
    BANG = "bang"
    CLOUD = "cloud"
    HEXAGON = "hexagon"


class ModwireMindmapTextFormat(StrEnum):
    PLAIN = "plain"
    MARKDOWN = "markdown"


class ModwireMindmapLayout(StrEnum):
    DEFAULT = ""
    TIDY_TREE = "tidy-tree"


class ModwireMindmapNode(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    label: ModwireMultilineText
    shape: ModwireMindmapShape = ModwireMindmapShape.DEFAULT
    text_format: ModwireMindmapTextFormat = ModwireMindmapTextFormat.PLAIN
    icon_classes: tuple[ModwireCssName, ...] = ()
    css_classes: tuple[ModwireCssName, ...] = ()
    children: tuple[ModwireMindmapNode, ...] = ()

    @model_validator(mode="after")
    def validate_node(self):
        if self.shape is ModwireMindmapShape.DEFAULT and self.text_format is ModwireMindmapTextFormat.MARKDOWN:
            raise contract_validation_error(
                type(self).__name__,
                (
                    ModwireContractViolation(
                        ("text_format",),
                        "invalid_configuration",
                        "Markdown mindmap nodes require an explicit shape",
                        self.text_format,
                    ),
                ),
            )
        if self.shape is ModwireMindmapShape.DEFAULT and self.id != self.label:
            raise contract_validation_error(
                type(self).__name__,
                (
                    ModwireContractViolation(
                        ("label",),
                        "invalid_configuration",
                        "Default-shaped mindmap nodes use their ID as the label",
                        self.label,
                    ),
                ),
            )
        if len(self.css_classes) != len(set(self.css_classes)):
            raise contract_validation_error(
                type(self).__name__,
                (
                    ModwireContractViolation(
                        ("css_classes",),
                        "duplicate_identifier",
                        "Mindmap node CSS classes must be unique",
                        self.css_classes,
                    ),
                ),
            )
        return self


class ModwireMindmap(ModwireBaseDiagram):
    kind: Literal["mindmap"] = "mindmap"
    docs_url = "https://mermaid.js.org/syntax/mindmap.html"
    syntax_features = (
        ModwireSyntaxFeature("classes", "test_mindmap_covers_all_documented_shapes_icons_classes_markdown_and_layout"),
        ModwireSyntaxFeature(
            "different-shapes", "test_mindmap_covers_all_documented_shapes_icons_classes_markdown_and_layout"
        ),
        ModwireSyntaxFeature("icons", "test_mindmap_covers_all_documented_shapes_icons_classes_markdown_and_layout"),
        ModwireSyntaxFeature(
            "markdown-strings", "test_mindmap_covers_all_documented_shapes_icons_classes_markdown_and_layout"
        ),
        ModwireSyntaxFeature("syntax", "test_mindmap_covers_all_documented_shapes_icons_classes_markdown_and_layout"),
    )

    root: ModwireMindmapNode
    layout: ModwireMindmapLayout = ModwireMindmapLayout.DEFAULT

    @model_validator(mode="after")
    def validate_tree(self):
        identifiers: list[str] = []
        self._validate_node(self.root, identifiers)
        self._validate_unique_children(identifiers, "Mindmap")
        return self

    def _validate_node(self, node: ModwireMindmapNode, identifiers: list[str]) -> None:
        identifiers.append(node.id)
        self._validate_unique_children((child.id for child in node.children), f"Mindmap node {node.id!r}")
        for child in node.children:
            self._validate_node(child, identifiers)
