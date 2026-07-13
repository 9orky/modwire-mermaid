import re
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, model_validator

from ..contracts import (
    MODWIRE_CALLBACK_PATTERN,
    MODWIRE_URL_PATTERN,
    ModwireBaseDiagram,
    ModwireContractViolation,
    ModwireCssName,
    ModwireDiagramContract,
    ModwireDiagramIdentifier,
    ModwireDiagramReference,
    ModwireMultilineText,
    ModwireNamespaceIdentifier,
    ModwireNamespaceReference,
    ModwireOptionalSyntaxToken,
    ModwireOptionalText,
    ModwireStyleName,
    ModwireStyleValue,
    ModwireSyntaxFeature,
    ModwireSyntaxToken,
    ModwireText,
    contract_validation_error,
)


class _ClassSyntax:
    @staticmethod
    def require_single_line(value: str, subject: str) -> str:
        if not value.strip() or any(character in value for character in "\r\n{}"):
            raise ValueError(f"{subject} must be a non-blank single line without braces")
        return value


class ModwireVisibility(StrEnum):
    PUBLIC = "+"
    PRIVATE = "-"
    PROTECTED = "#"
    PACKAGE = "~"


class ModwireMemberClassifier(StrEnum):
    ABSTRACT = "*"
    STATIC = "$"


class ModwireClassAttribute(ModwireDiagramContract):
    member_type: Literal["attribute"] = "attribute"
    name: ModwireSyntaxToken
    type: ModwireSyntaxToken
    visibility: ModwireVisibility = ModwireVisibility.PUBLIC
    is_static: bool = False

    @model_validator(mode="after")
    def validate_attribute(self):
        _ClassSyntax.require_single_line(self.name, "Attribute name")
        _ClassSyntax.require_single_line(self.type, "Attribute type")
        return self


class ModwireClassParameter(ModwireDiagramContract):
    name: ModwireSyntaxToken
    type: ModwireSyntaxToken

    @model_validator(mode="after")
    def validate_parameter(self):
        _ClassSyntax.require_single_line(self.name, "Parameter name")
        _ClassSyntax.require_single_line(self.type, "Parameter type")
        return self


class ModwireClassMethod(ModwireDiagramContract):
    member_type: Literal["method"] = "method"
    name: ModwireSyntaxToken
    parameters: tuple[ModwireClassParameter, ...] = ()
    return_type: ModwireSyntaxToken
    visibility: ModwireVisibility = ModwireVisibility.PUBLIC
    classifiers: tuple[ModwireMemberClassifier, ...] = ()

    @model_validator(mode="after")
    def validate_method(self):
        _ClassSyntax.require_single_line(self.name, "Method name")
        _ClassSyntax.require_single_line(self.return_type, "Method return type")
        if len(self.classifiers) != len(set(self.classifiers)):
            raise contract_validation_error(
                type(self).__name__,
                (
                    ModwireContractViolation(
                        ("classifiers",),
                        "duplicate_identifier",
                        "Method classifiers must be unique",
                        self.classifiers,
                    ),
                ),
            )
        return self


ModwireClassMember = Annotated[ModwireClassAttribute | ModwireClassMethod, Field(discriminator="member_type")]


class ModwireClass(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    label: ModwireText
    members: tuple[ModwireClassMember, ...] = ()
    annotations: tuple[ModwireSyntaxToken, ...] = ()
    namespace: ModwireNamespaceReference = ""
    generic_type: ModwireOptionalSyntaxToken = ""
    css_classes: tuple[ModwireCssName, ...] = ()

    @model_validator(mode="after")
    def validate_class(self):
        _ClassSyntax.require_single_line(self.label, "Class label")
        for index, annotation in enumerate(self.annotations):
            _ClassSyntax.require_single_line(annotation, "Class annotation")
            if "<<" in annotation or ">>" in annotation:
                raise contract_validation_error(
                    type(self).__name__,
                    (
                        ModwireContractViolation(
                            ("annotations", index),
                            "invalid_configuration",
                            "Class annotations must not include angle delimiters",
                            annotation,
                        ),
                    ),
                )
        if self.namespace:
            _ClassSyntax.require_single_line(self.namespace, "Class namespace")
        if self.generic_type:
            _ClassSyntax.require_single_line(self.generic_type, "Class generic type")
            if "," in self.generic_type:
                raise contract_validation_error(
                    type(self).__name__,
                    (
                        ModwireContractViolation(
                            ("generic_type",),
                            "invalid_configuration",
                            "Mermaid generic types cannot contain commas",
                            self.generic_type,
                        ),
                    ),
                )
        for css_class in self.css_classes:
            _ClassSyntax.require_single_line(css_class, "CSS class")
        return self


class ModwireRelationshipEnd(StrEnum):
    NONE = ""
    INHERITANCE = "<|"
    COMPOSITION = "*"
    AGGREGATION = "o"
    ASSOCIATION_RIGHT = ">"
    ASSOCIATION_LEFT = "<"
    REALIZATION = "|>"
    LOLLIPOP = "()"


class ModwireRelationshipLine(StrEnum):
    SOLID = "--"
    DASHED = ".."


class ModwireClassRelationship(ModwireDiagramContract):
    source: ModwireDiagramIdentifier
    target: ModwireDiagramIdentifier
    source_end: ModwireRelationshipEnd = ModwireRelationshipEnd.NONE
    line: ModwireRelationshipLine = ModwireRelationshipLine.SOLID
    target_end: ModwireRelationshipEnd = ModwireRelationshipEnd.NONE
    label: ModwireOptionalText = ""
    source_cardinality: ModwireOptionalText = ""
    target_cardinality: ModwireOptionalText = ""

    @model_validator(mode="after")
    def validate_relationship(self):
        if self.label:
            _ClassSyntax.require_single_line(self.label, "Relationship label")
        for cardinality in (self.source_cardinality, self.target_cardinality):
            if cardinality:
                _ClassSyntax.require_single_line(cardinality, "Relationship cardinality")
        if self.source_end is ModwireRelationshipEnd.LOLLIPOP and self.target_end is ModwireRelationshipEnd.LOLLIPOP:
            raise contract_validation_error(
                type(self).__name__,
                (
                    ModwireContractViolation(
                        ("target_end",),
                        "invalid_configuration",
                        "A lollipop relationship must contain exactly one interface end",
                        self.target_end,
                    ),
                ),
            )
        return self


class ModwireClassNote(ModwireDiagramContract):
    class_id: ModwireDiagramReference = ""
    text: ModwireMultilineText

    @model_validator(mode="after")
    def validate_note(self):
        if not self.text.strip():
            raise contract_validation_error(
                type(self).__name__,
                (ModwireContractViolation(("text",), "text_blank", "Class note cannot be blank", self.text),),
            )
        return self


class ModwireClassInteractionKind(StrEnum):
    LINK = "link"
    CALLBACK = "callback"


class ModwireClassInteractionSyntax(StrEnum):
    ACTION = "action"
    CLICK = "click"


class ModwireClassInteraction(ModwireDiagramContract):
    class_id: ModwireDiagramIdentifier
    kind: ModwireClassInteractionKind
    reference: ModwireText
    tooltip: ModwireOptionalText = ""
    syntax: ModwireClassInteractionSyntax = ModwireClassInteractionSyntax.ACTION

    @model_validator(mode="after")
    def validate_interaction(self):
        _ClassSyntax.require_single_line(self.reference, "Class interaction reference")
        if self.tooltip:
            _ClassSyntax.require_single_line(self.tooltip, "Class interaction tooltip")
        pattern = MODWIRE_CALLBACK_PATTERN if self.kind is ModwireClassInteractionKind.CALLBACK else MODWIRE_URL_PATTERN
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


class ModwireClassNamespace(ModwireDiagramContract):
    id: ModwireNamespaceIdentifier
    label: ModwireOptionalText = ""

    @model_validator(mode="after")
    def validate_namespace(self):
        _ClassSyntax.require_single_line(self.id, "Namespace identifier")
        if self.label:
            _ClassSyntax.require_single_line(self.label, "Namespace label")
        return self


class ModwireClassStyleProperty(ModwireDiagramContract):
    name: ModwireStyleName
    value: ModwireStyleValue

    @model_validator(mode="after")
    def validate_property(self):
        _ClassSyntax.require_single_line(self.name, "Style property name")
        _ClassSyntax.require_single_line(self.value, "Style property value")
        return self


class ModwireClassStyle(ModwireDiagramContract):
    class_id: ModwireDiagramIdentifier
    properties: tuple[ModwireClassStyleProperty, ...] = ()


class ModwireClassStyleDefinition(ModwireDiagramContract):
    names: tuple[ModwireCssName, ...]
    properties: tuple[ModwireClassStyleProperty, ...] = ()

    @model_validator(mode="after")
    def validate_definition(self):
        if not self.names:
            raise contract_validation_error(
                type(self).__name__,
                (
                    ModwireContractViolation(
                        ("names",), "missing_child", "Style definition must have at least one name", self.names
                    ),
                ),
            )
        for name in self.names:
            _ClassSyntax.require_single_line(name, "Style definition name")
        return self


class ModwireClassDiagramDirection(StrEnum):
    TOP_BOTTOM = "TB"
    BOTTOM_TOP = "BT"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"


class ModwireClassDiagram(ModwireBaseDiagram):
    kind: Literal["class"] = "class"
    docs_url = "https://mermaid.js.org/syntax/classDiagram.html"
    syntax_features = (
        ModwireSyntaxFeature("annotations-on-classes", "test_class_diagram_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("class", "test_class_diagram_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("comments", "test_class_diagram_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("define-a-class", "test_class_diagram_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("define-namespace", "test_class_diagram_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("defining-members-of-a-class", "test_class_diagram_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("defining-relationship", "test_class_diagram_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("interaction", "test_class_diagram_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("setting-the-direction-of-the-diagram", "test_class_diagram_covers_rich_mermaid_syntax"),
        ModwireSyntaxFeature("styling", "test_class_diagram_covers_rich_mermaid_syntax"),
    )

    classes: tuple[ModwireClass, ...]
    relationships: tuple[ModwireClassRelationship, ...] = ()
    direction: ModwireClassDiagramDirection = ModwireClassDiagramDirection.TOP_BOTTOM
    comments: tuple[ModwireText, ...] = ()
    notes: tuple[ModwireClassNote, ...] = ()
    interactions: tuple[ModwireClassInteraction, ...] = ()
    namespaces: tuple[ModwireClassNamespace, ...] = ()
    styles: tuple[ModwireClassStyle, ...] = ()
    style_definitions: tuple[ModwireClassStyleDefinition, ...] = ()
    hide_empty_members_box: bool = False
    hierarchical_namespaces: bool = False

    @model_validator(mode="after")
    def validate_graph(self):
        identifiers = tuple(item.id for item in self.classes)
        self._require_children(self.classes, "Class diagram")
        self._validate_unique_children(identifiers, "Class diagram")
        references: list[tuple[tuple[str | int, ...], str]] = []
        lollipop_interfaces: list[str] = []
        for index, relation in enumerate(self.relationships):
            if relation.source_end is ModwireRelationshipEnd.LOLLIPOP:
                lollipop_interfaces.append(relation.source)
            else:
                references.append((("relationships", index, "source"), relation.source))
            if relation.target_end is ModwireRelationshipEnd.LOLLIPOP:
                lollipop_interfaces.append(relation.target)
            else:
                references.append((("relationships", index, "target"), relation.target))
        self._validate_unique_children(lollipop_interfaces, "Lollipop interface")
        references.extend(
            (("notes", index, "class_id"), note.class_id) for index, note in enumerate(self.notes) if note.class_id
        )
        references.extend(
            (("interactions", index, "class_id"), interaction.class_id)
            for index, interaction in enumerate(self.interactions)
        )
        references.extend((("styles", index, "class_id"), style.class_id) for index, style in enumerate(self.styles))
        self._validate_located_references(identifiers, references, "Class")
        namespace_ids = tuple(namespace.id for namespace in self.namespaces)
        self._validate_unique_children(namespace_ids, "Class namespace")
        self._validate_located_references(
            namespace_ids,
            (
                (("classes", index, "namespace"), item.namespace)
                for index, item in enumerate(self.classes)
                if item.namespace
            ),
            "Class namespace",
        )
        style_names = tuple(name for item in self.style_definitions for name in item.names)
        self._validate_unique_children(style_names, "Class style definition")
        for comment in self.comments:
            _ClassSyntax.require_single_line(comment, "Class diagram comment")
        return self
