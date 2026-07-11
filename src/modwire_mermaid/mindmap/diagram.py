from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from ..contracts import ModwireBaseDiagram, ModwireDiagramContract, ModwireDiagramError, ModwireSyntaxFeature


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
    id: str
    label: str
    shape: ModwireMindmapShape
    text_format: ModwireMindmapTextFormat
    icon_classes: tuple[str, ...]
    css_classes: tuple[str, ...]
    children: tuple[ModwireMindmapNode, ...]

    @model_validator(mode="after")
    def validate_node(self):
        if not self.id.strip() or any(character in self.id for character in "\r\n()[]{}"):
            raise ModwireDiagramError("Mindmap node IDs must be non-blank and cannot contain shape delimiters")
        if not self.label.strip():
            raise ModwireDiagramError("Mindmap node labels cannot be blank")
        if self.shape is ModwireMindmapShape.DEFAULT and self.text_format is ModwireMindmapTextFormat.MARKDOWN:
            raise ModwireDiagramError("Markdown mindmap nodes require an explicit shape")
        if self.shape is ModwireMindmapShape.DEFAULT and self.id != self.label:
            raise ModwireDiagramError("Default-shaped mindmap nodes use their ID as the label")
        if len(self.css_classes) != len(set(self.css_classes)):
            raise ModwireDiagramError("Mindmap node CSS classes must be unique")
        return self


class ModwireMindmap(ModwireBaseDiagram):
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
    layout: ModwireMindmapLayout

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
