from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from ..contracts import (
    ModwireBaseDiagram,
    ModwireConfigValue,
    ModwireContractViolation,
    ModwireCssName,
    ModwireDiagramContract,
    ModwireIconName,
    ModwireOptionalIconName,
    ModwireOptionalText,
    ModwireSyntaxFeature,
    ModwireText,
    contract_validation_error,
)


class ModwireFileTreeIconMapping(ModwireDiagramContract):
    pattern: ModwireText
    icon: ModwireIconName


class ModwireFileTreeNode(ModwireDiagramContract):
    label: ModwireText
    is_directory: bool
    description: ModwireOptionalText = ""
    icon: ModwireOptionalIconName = ""
    css_classes: tuple[ModwireCssName, ...] = ()
    children: tuple[ModwireFileTreeNode, ...] = ()

    @model_validator(mode="after")
    def validate_node(self):
        if self.children and not self.is_directory:
            raise contract_validation_error(
                type(self).__name__,
                (
                    ModwireContractViolation(
                        ("children",),
                        "invalid_configuration",
                        "File-tree files cannot contain children",
                        self.children,
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
                        "File-tree CSS classes must be unique",
                        self.css_classes,
                    ),
                ),
            )
        return self


class ModwireFileTree(ModwireBaseDiagram):
    kind: Literal["file-tree"] = "file-tree"
    docs_url = "https://mermaid.js.org/syntax/treeView.html"
    syntax_features = (
        ModwireSyntaxFeature("config-variables", "test_file_tree_builds_safe_sorted_tree"),
        ModwireSyntaxFeature("icons", "test_file_tree_builds_safe_sorted_tree"),
        ModwireSyntaxFeature("syntax", "test_file_tree_builds_safe_sorted_tree"),
        ModwireSyntaxFeature("theme-variables", "test_file_tree_builds_safe_sorted_tree"),
    )

    root: ModwireFileTreeNode
    comments: tuple[ModwireText, ...] = ()
    row_indent: int = Field(default=10, ge=0)
    padding_x: int = Field(default=5, ge=0)
    padding_y: int = Field(default=5, ge=0)
    line_thickness: int = Field(default=1, ge=0)
    show_icons: bool = True
    default_icon_pack: ModwireOptionalText = ""
    filename_icons: tuple[ModwireFileTreeIconMapping, ...] = ()
    extension_icons: tuple[ModwireFileTreeIconMapping, ...] = ()
    label_font_size: ModwireConfigValue = "16px"
    label_color: ModwireConfigValue = "currentColor"
    line_color: ModwireConfigValue = "currentColor"
    icon_color: ModwireConfigValue = "currentColor"
    description_color: ModwireConfigValue = "currentColor"
    highlight_background: ModwireConfigValue = "transparent"
    highlight_stroke: ModwireConfigValue = "currentColor"

    @model_validator(mode="after")
    def validate_tree(self):
        if not self.root.is_directory:
            raise contract_validation_error(
                type(self).__name__,
                (
                    ModwireContractViolation(
                        ("root", "is_directory"),
                        "invalid_configuration",
                        "File-tree root must be a directory",
                        self.root.is_directory,
                    ),
                ),
            )
        self._validate_node(self.root)
        self._validate_unique_children((item.pattern for item in self.filename_icons), "Filename icon mapping")
        self._validate_unique_children((item.pattern for item in self.extension_icons), "Extension icon mapping")
        return self

    def _validate_node(self, node: ModwireFileTreeNode) -> None:
        self._validate_unique_children((child.label for child in node.children), f"File-tree node {node.label!r}")
        for child in node.children:
            self._validate_node(child)
