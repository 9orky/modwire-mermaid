from enum import StrEnum

from pydantic import model_validator

from ..contracts import (
    ModwireBaseDiagram,
    ModwireDiagramContract,
    ModwireDiagramError,
    ModwireDiagramIdentifier,
    ModwireSyntaxFeature,
)


class _ClassSyntax:
    @staticmethod
    def require_single_line(value: str, subject: str) -> str:
        if not value.strip() or any(character in value for character in "\r\n{}"):
            raise ModwireDiagramError(f"{subject} must be a non-blank single line without braces")
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
    name: str
    type: str
    visibility: ModwireVisibility
    is_static: bool

    @model_validator(mode="after")
    def validate_attribute(self):
        _ClassSyntax.require_single_line(self.name, "Attribute name")
        _ClassSyntax.require_single_line(self.type, "Attribute type")
        return self

    def mermaid(self) -> str:
        return f"{self.visibility.value}{self.type} {self.name}{'$' if self.is_static else ''}"


class ModwireClassParameter(ModwireDiagramContract):
    name: str
    type: str

    @model_validator(mode="after")
    def validate_parameter(self):
        _ClassSyntax.require_single_line(self.name, "Parameter name")
        _ClassSyntax.require_single_line(self.type, "Parameter type")
        return self

    def mermaid(self) -> str:
        return f"{self.name}: {self.type}"


class ModwireClassMethod(ModwireDiagramContract):
    name: str
    parameters: tuple[ModwireClassParameter, ...]
    return_type: str
    visibility: ModwireVisibility
    classifiers: tuple[ModwireMemberClassifier, ...]

    @model_validator(mode="after")
    def validate_method(self):
        _ClassSyntax.require_single_line(self.name, "Method name")
        _ClassSyntax.require_single_line(self.return_type, "Method return type")
        if len(self.classifiers) != len(set(self.classifiers)):
            raise ModwireDiagramError("Method classifiers must be unique")
        return self

    def mermaid(self) -> str:
        parameters = ", ".join(parameter.mermaid() for parameter in self.parameters)
        classifiers = "".join(value.value for value in self.classifiers)
        return f"{self.visibility.value}{self.name}({parameters}) {self.return_type}{classifiers}"


ModwireClassMember = ModwireClassAttribute | ModwireClassMethod


class ModwireClass(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    label: str
    members: tuple[ModwireClassMember, ...]
    annotations: tuple[str, ...]
    namespace: str
    generic_type: str
    css_classes: tuple[str, ...]

    @model_validator(mode="after")
    def validate_class(self):
        _ClassSyntax.require_single_line(self.label, "Class label")
        for annotation in self.annotations:
            _ClassSyntax.require_single_line(annotation, "Class annotation")
            if "<<" in annotation or ">>" in annotation:
                raise ModwireDiagramError("Class annotations must not include angle delimiters")
        if self.namespace:
            _ClassSyntax.require_single_line(self.namespace, "Class namespace")
        if self.generic_type:
            _ClassSyntax.require_single_line(self.generic_type, "Class generic type")
            if "," in self.generic_type:
                raise ModwireDiagramError("Mermaid generic types cannot contain commas")
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
    source_end: ModwireRelationshipEnd
    line: ModwireRelationshipLine
    target_end: ModwireRelationshipEnd
    label: str
    source_cardinality: str
    target_cardinality: str

    @model_validator(mode="after")
    def validate_relationship(self):
        if self.label:
            _ClassSyntax.require_single_line(self.label, "Relationship label")
        for cardinality in (self.source_cardinality, self.target_cardinality):
            if cardinality:
                _ClassSyntax.require_single_line(cardinality, "Relationship cardinality")
        if self.source_end is ModwireRelationshipEnd.LOLLIPOP and self.target_end is ModwireRelationshipEnd.LOLLIPOP:
            raise ModwireDiagramError("A lollipop relationship must contain exactly one interface end")
        return self

    def mermaid_arrow(self) -> str:
        return f"{self.source_end.value}{self.line.value}{self.target_end.value}"


class ModwireClassNote(ModwireDiagramContract):
    class_id: str
    text: str

    @model_validator(mode="after")
    def validate_note(self):
        if not self.text.strip():
            raise ModwireDiagramError("Class note cannot be blank")
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
    reference: str
    tooltip: str
    syntax: ModwireClassInteractionSyntax

    @model_validator(mode="after")
    def validate_interaction(self):
        _ClassSyntax.require_single_line(self.reference, "Class interaction reference")
        if self.tooltip:
            _ClassSyntax.require_single_line(self.tooltip, "Class interaction tooltip")
        return self


class ModwireClassNamespace(ModwireDiagramContract):
    id: str
    label: str

    @model_validator(mode="after")
    def validate_namespace(self):
        _ClassSyntax.require_single_line(self.id, "Namespace identifier")
        if self.label:
            _ClassSyntax.require_single_line(self.label, "Namespace label")
        return self


class ModwireClassStyleProperty(ModwireDiagramContract):
    name: str
    value: str

    @model_validator(mode="after")
    def validate_property(self):
        _ClassSyntax.require_single_line(self.name, "Style property name")
        _ClassSyntax.require_single_line(self.value, "Style property value")
        if any(character in self.name for character in ":,;"):
            raise ModwireDiagramError("Style property names cannot contain separators")
        return self

    def mermaid(self) -> str:
        return f"{self.name}:{self.value}"


class ModwireClassStyle(ModwireDiagramContract):
    class_id: ModwireDiagramIdentifier
    properties: tuple[ModwireClassStyleProperty, ...]


class ModwireClassStyleDefinition(ModwireDiagramContract):
    names: tuple[str, ...]
    properties: tuple[ModwireClassStyleProperty, ...]

    @model_validator(mode="after")
    def validate_definition(self):
        if not self.names:
            raise ModwireDiagramError("Style definition must have at least one name")
        for name in self.names:
            _ClassSyntax.require_single_line(name, "Style definition name")
        return self


class ModwireClassDiagramDirection(StrEnum):
    TOP_BOTTOM = "TB"
    BOTTOM_TOP = "BT"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"


class ModwireClassDiagram(ModwireBaseDiagram):
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
    relationships: tuple[ModwireClassRelationship, ...]
    direction: ModwireClassDiagramDirection
    comments: tuple[str, ...]
    notes: tuple[ModwireClassNote, ...]
    interactions: tuple[ModwireClassInteraction, ...]
    namespaces: tuple[ModwireClassNamespace, ...]
    styles: tuple[ModwireClassStyle, ...]
    style_definitions: tuple[ModwireClassStyleDefinition, ...]
    hide_empty_members_box: bool
    hierarchical_namespaces: bool

    @model_validator(mode="after")
    def validate_graph(self):
        identifiers = tuple(item.id for item in self.classes)
        self._require_children(self.classes, "Class diagram")
        self._validate_unique_children(identifiers, "Class diagram")
        references = []
        lollipop_interfaces = []
        for relation in self.relationships:
            if relation.source_end is ModwireRelationshipEnd.LOLLIPOP:
                lollipop_interfaces.append(relation.source)
            else:
                references.append(relation.source)
            if relation.target_end is ModwireRelationshipEnd.LOLLIPOP:
                lollipop_interfaces.append(relation.target)
            else:
                references.append(relation.target)
        self._validate_unique_children(lollipop_interfaces, "Lollipop interface")
        references.extend(note.class_id for note in self.notes if note.class_id)
        references.extend(interaction.class_id for interaction in self.interactions)
        references.extend(style.class_id for style in self.styles)
        self._validate_child_references(identifiers, references, "Class relationship, note, or interaction")
        namespace_ids = tuple(namespace.id for namespace in self.namespaces)
        self._validate_unique_children(namespace_ids, "Class namespace")
        unknown_namespaces = {item.namespace for item in self.classes if item.namespace} - set(namespace_ids)
        if unknown_namespaces:
            raise ModwireDiagramError(f"Classes reference unknown namespaces: {sorted(unknown_namespaces)}")
        style_names = tuple(name for item in self.style_definitions for name in item.names)
        self._validate_unique_children(style_names, "Class style definition")
        for comment in self.comments:
            _ClassSyntax.require_single_line(comment, "Class diagram comment")
        return self
