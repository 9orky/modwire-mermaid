from __future__ import annotations

from pydantic import Field, model_validator

from ..contracts import ModwireBaseDiagram, ModwireDiagramContract, ModwireDiagramError, ModwireSyntaxFeature


class ModwireFileTreeIconMapping(ModwireDiagramContract):
    pattern: str
    icon: str


class ModwireFileTreeNode(ModwireDiagramContract):
    label: str
    is_directory: bool
    description: str
    icon: str
    css_classes: tuple[str, ...]
    children: tuple[ModwireFileTreeNode, ...]

    @model_validator(mode="after")
    def validate_node(self):
        if not self.label.strip() or any(character in self.label for character in "\r\n"):
            raise ModwireDiagramError("File-tree labels must be non-blank single lines")
        if self.description and any(character in self.description for character in "\r\n"):
            raise ModwireDiagramError("File-tree descriptions must be single lines")
        if self.children and not self.is_directory:
            raise ModwireDiagramError("File-tree files cannot contain children")
        if len(self.css_classes) != len(set(self.css_classes)):
            raise ModwireDiagramError("File-tree CSS classes must be unique")
        return self


class ModwireFileTree(ModwireBaseDiagram):
    docs_url = "https://mermaid.js.org/syntax/treeView.html"
    syntax_features = (
        ModwireSyntaxFeature("config-variables", "test_file_tree_builds_safe_sorted_tree"),
        ModwireSyntaxFeature("icons", "test_file_tree_builds_safe_sorted_tree"),
        ModwireSyntaxFeature("syntax", "test_file_tree_builds_safe_sorted_tree"),
        ModwireSyntaxFeature("theme-variables", "test_file_tree_builds_safe_sorted_tree"),
    )

    root: ModwireFileTreeNode
    comments: tuple[str, ...]
    row_indent: int = Field(ge=0)
    padding_x: int = Field(ge=0)
    padding_y: int = Field(ge=0)
    line_thickness: int = Field(ge=0)
    show_icons: bool
    default_icon_pack: str
    filename_icons: tuple[ModwireFileTreeIconMapping, ...]
    extension_icons: tuple[ModwireFileTreeIconMapping, ...]
    label_font_size: str
    label_color: str
    line_color: str
    icon_color: str
    description_color: str
    highlight_background: str
    highlight_stroke: str

    @model_validator(mode="after")
    def validate_tree(self):
        if not self.root.is_directory:
            raise ModwireDiagramError("File-tree root must be a directory")
        self._validate_node(self.root)
        for comment in self.comments:
            if not comment.strip() or any(character in comment for character in "\r\n"):
                raise ModwireDiagramError("File-tree comments must be non-blank single lines")
        self._validate_unique_children((item.pattern for item in self.filename_icons), "Filename icon mapping")
        self._validate_unique_children((item.pattern for item in self.extension_icons), "Extension icon mapping")
        return self

    def _validate_node(self, node: ModwireFileTreeNode) -> None:
        self._validate_unique_children((child.label for child in node.children), f"File-tree node {node.label!r}")
        for child in node.children:
            self._validate_node(child)
