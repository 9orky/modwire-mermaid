import pytest
from pydantic import ValidationError

from modwire_mermaid.class_diagram.diagram import (
    ModwireClass,
    ModwireClassAttribute,
    ModwireClassDiagram,
    ModwireClassDiagramDirection,
    ModwireClassInteraction,
    ModwireClassInteractionKind,
    ModwireClassInteractionSyntax,
    ModwireClassMethod,
    ModwireClassNamespace,
    ModwireClassNote,
    ModwireClassRelationship,
    ModwireClassStyle,
    ModwireClassStyleDefinition,
    ModwireClassStyleProperty,
    ModwireMemberClassifier,
    ModwireRelationshipEnd,
    ModwireRelationshipLine,
    ModwireVisibility,
)
from modwire_mermaid.composition import (
    ModwireMermaidFactory,
)
from modwire_mermaid.file_tree.diagram import (
    ModwireFileTree,
    ModwireFileTreeIconMapping,
    ModwireFileTreeNode,
)
from modwire_mermaid.graph import (
    ModwireFlowchart,
    ModwireFlowchartAnimation,
    ModwireFlowchartCurve,
    ModwireFlowchartDirection,
    ModwireFlowchartEdge,
    ModwireFlowchartEdgeEnd,
    ModwireFlowchartEdgeLine,
    ModwireFlowchartIconForm,
    ModwireFlowchartIconNode,
    ModwireFlowchartImageConstraint,
    ModwireFlowchartImageNode,
    ModwireFlowchartInteraction,
    ModwireFlowchartInteractionKind,
    ModwireFlowchartLabelPosition,
    ModwireFlowchartLinkStyle,
    ModwireFlowchartLinkTarget,
    ModwireFlowchartNode,
    ModwireFlowchartNodeStyle,
    ModwireFlowchartShape,
    ModwireFlowchartStyleDefinition,
    ModwireFlowchartStyleProperty,
    ModwireFlowchartSubgraph,
    ModwireFlowchartTextFormat,
)
from modwire_mermaid.mindmap.diagram import (
    ModwireMindmap,
    ModwireMindmapLayout,
    ModwireMindmapNode,
    ModwireMindmapShape,
    ModwireMindmapTextFormat,
)


def test_flowchart_is_typed_validated_and_deterministic():
    diagram = ModwireFlowchart(
        nodes=(
            ModwireFlowchartNode(
                id="request",
                label="Request",
                shape=ModwireFlowchartShape.PROCESS,
                text_format=ModwireFlowchartTextFormat.PLAIN,
                css_classes=(),
            ),
            ModwireFlowchartNode(
                id="use_case",
                label='Execute "case"',
                shape=ModwireFlowchartShape.PROCESS,
                text_format=ModwireFlowchartTextFormat.PLAIN,
                css_classes=(),
            ),
        ),
        edges=(
            ModwireFlowchartEdge(
                id="",
                source="request",
                target="use_case",
                label="dispatch",
                text_format=ModwireFlowchartTextFormat.PLAIN,
                line=ModwireFlowchartEdgeLine.NORMAL,
                source_end=ModwireFlowchartEdgeEnd.NONE,
                target_end=ModwireFlowchartEdgeEnd.ARROW,
                minimum_length=1,
                animation=ModwireFlowchartAnimation.NONE,
                curve=ModwireFlowchartCurve.DEFAULT,
                css_classes=(),
            ),
        ),
        subgraphs=(),
        direction=ModwireFlowchartDirection.LEFT_RIGHT,
        interactions=(),
        node_styles=(),
        link_styles=(),
        style_definitions=(),
        comments=(),
        markdown_auto_wrap=True,
        default_curve=ModwireFlowchartCurve.LINEAR,
    )

    source = ModwireMermaidFactory.standard().compile(diagram)

    assert "flowchart LR\n" in source
    assert 'request@{ shape: rect, label: "Request" }' in source
    assert 'request -->|"dispatch"| use_case' in source


def test_flowchart_rejects_dangling_edges():
    with pytest.raises(ValidationError, match="does not exist"):
        ModwireFlowchart(
            nodes=(
                ModwireFlowchartNode(
                    id="known",
                    label="Known",
                    shape=ModwireFlowchartShape.PROCESS,
                    text_format=ModwireFlowchartTextFormat.PLAIN,
                    css_classes=(),
                ),
            ),
            edges=(
                ModwireFlowchartEdge(
                    id="",
                    source="known",
                    target="missing",
                    label="unknown",
                    text_format=ModwireFlowchartTextFormat.PLAIN,
                    line=ModwireFlowchartEdgeLine.NORMAL,
                    source_end=ModwireFlowchartEdgeEnd.NONE,
                    target_end=ModwireFlowchartEdgeEnd.ARROW,
                    minimum_length=1,
                    animation=ModwireFlowchartAnimation.NONE,
                    curve=ModwireFlowchartCurve.DEFAULT,
                    css_classes=(),
                ),
            ),
            subgraphs=(),
            direction=ModwireFlowchartDirection.LEFT_RIGHT,
            interactions=(),
            node_styles=(),
            link_styles=(),
            style_definitions=(),
            comments=(),
            markdown_auto_wrap=True,
            default_curve=ModwireFlowchartCurve.LINEAR,
        )


def test_flowchart_supports_mermaid_identifiers_and_rejects_reserved_end():
    node = ModwireFlowchartNode(
        id="Use-猫",
        label="Use case",
        shape=ModwireFlowchartShape.PROCESS,
        text_format=ModwireFlowchartTextFormat.PLAIN,
        css_classes=(),
    )
    assert node.id == "Use-猫"

    with pytest.raises(ValidationError, match="reserved"):
        ModwireFlowchartNode(
            id="end",
            label="End",
            shape=ModwireFlowchartShape.PROCESS,
            text_format=ModwireFlowchartTextFormat.PLAIN,
            css_classes=(),
        )


def test_flowchart_covers_rich_mermaid_syntax():
    stroke = ModwireFlowchartStyleProperty(name="stroke", value="#333")
    diagram = ModwireFlowchart(
        nodes=(
            ModwireFlowchartNode(
                id="decision",
                label="**Continue?**",
                shape=ModwireFlowchartShape.DECISION,
                text_format=ModwireFlowchartTextFormat.MARKDOWN,
                css_classes=("important",),
            ),
            ModwireFlowchartIconNode(
                id="service",
                icon="fa:fa-cloud",
                form=ModwireFlowchartIconForm.ROUNDED,
                label="Service",
                position=ModwireFlowchartLabelPosition.BOTTOM,
                height=48,
                css_classes=(),
            ),
            ModwireFlowchartImageNode(
                id="result",
                image_url="https://example.com/result.png",
                label="Result",
                position=ModwireFlowchartLabelPosition.TOP,
                width=60,
                height=60,
                constraint=ModwireFlowchartImageConstraint.ON,
                css_classes=(),
            ),
        ),
        edges=(
            ModwireFlowchartEdge(
                id="request_edge",
                source="decision",
                target="service",
                label="yes",
                text_format=ModwireFlowchartTextFormat.PLAIN,
                line=ModwireFlowchartEdgeLine.THICK,
                source_end=ModwireFlowchartEdgeEnd.CIRCLE,
                target_end=ModwireFlowchartEdgeEnd.CROSS,
                minimum_length=2,
                animation=ModwireFlowchartAnimation.FAST,
                curve=ModwireFlowchartCurve.STEP_BEFORE,
                css_classes=("animated",),
            ),
            ModwireFlowchartEdge(
                id="",
                source="service",
                target="result",
                label="",
                text_format=ModwireFlowchartTextFormat.PLAIN,
                line=ModwireFlowchartEdgeLine.DOTTED,
                source_end=ModwireFlowchartEdgeEnd.ARROW,
                target_end=ModwireFlowchartEdgeEnd.ARROW,
                minimum_length=3,
                animation=ModwireFlowchartAnimation.NONE,
                curve=ModwireFlowchartCurve.DEFAULT,
                css_classes=(),
            ),
        ),
        subgraphs=(
            ModwireFlowchartSubgraph(
                id="system",
                label="System",
                direction=ModwireFlowchartDirection.TOP_BOTTOM,
                node_ids=("decision",),
                children=(
                    ModwireFlowchartSubgraph(
                        id="backend",
                        label="Backend",
                        direction=ModwireFlowchartDirection.LEFT_RIGHT,
                        node_ids=("service",),
                        children=(),
                    ),
                ),
            ),
        ),
        direction=ModwireFlowchartDirection.LEFT_RIGHT,
        interactions=(
            ModwireFlowchartInteraction(
                node_id="result",
                kind=ModwireFlowchartInteractionKind.LINK,
                reference="https://example.com",
                tooltip="Open result",
                link_target=ModwireFlowchartLinkTarget.BLANK,
            ),
        ),
        node_styles=(ModwireFlowchartNodeStyle(node_id="decision", properties=(stroke,)),),
        link_styles=(ModwireFlowchartLinkStyle(edge_indexes=(1,), use_default=False, properties=(stroke,)),),
        style_definitions=(ModwireFlowchartStyleDefinition(names=("important", "animated"), properties=(stroke,)),),
        comments=("rich flowchart",),
        markdown_auto_wrap=False,
        default_curve=ModwireFlowchartCurve.CARDINAL,
    )

    source = ModwireMermaidFactory.standard().compile(diagram)

    assert "markdownAutoWrap: false" in source
    assert "curve: cardinal" in source
    assert 'decision@{ shape: diam, label: "`**Continue?**`" }' in source
    assert 'service@{ icon: "fa:fa-cloud"' in source
    assert 'result@{ img: "https://example.com/result.png"' in source
    assert 'subgraph system["System"]' in source
    assert 'subgraph backend["Backend"]' in source
    assert 'decision request_edge@o===x|"yes"| service' in source
    assert "request_edge@{ animate: true, animation: fast, curve: stepBefore }" in source
    assert "service <-...-> result" in source
    assert 'click result href "https://example.com" "Open result" _blank' in source
    assert "linkStyle 1 stroke:#333;" in source
    assert "classDef important,animated stroke:#333;" in source


def test_class_diagram_owns_members_and_relationship_syntax():
    diagram = ModwireClassDiagram(
        classes=(
            ModwireClass(
                id="UseCase",
                label="Use Case",
                members=(
                    ModwireClassMethod(
                        name="execute",
                        parameters=(),
                        return_type="Result",
                        visibility=ModwireVisibility.PUBLIC,
                        classifiers=(),
                    ),
                ),
                annotations=(),
                namespace="",
                generic_type="T",
                css_classes=(),
            ),
            ModwireClass(
                id="Policy",
                label="Policy",
                members=(),
                annotations=(),
                namespace="domain.policy",
                generic_type="",
                css_classes=(),
            ),
        ),
        relationships=(
            ModwireClassRelationship(
                source="UseCase",
                target="Policy",
                source_end=ModwireRelationshipEnd.NONE,
                line=ModwireRelationshipLine.DASHED,
                target_end=ModwireRelationshipEnd.ASSOCIATION_RIGHT,
                label="uses",
                source_cardinality="",
                target_cardinality="",
            ),
        ),
        direction=ModwireClassDiagramDirection.TOP_BOTTOM,
        comments=(),
        notes=(),
        interactions=(
            ModwireClassInteraction(
                class_id="UseCase",
                kind=ModwireClassInteractionKind.LINK,
                reference="https://example.com/use-case",
                tooltip="Open documentation",
                syntax=ModwireClassInteractionSyntax.ACTION,
            ),
        ),
        namespaces=(ModwireClassNamespace(id="domain.policy", label="Domain policies"),),
        styles=(),
        style_definitions=(),
        hide_empty_members_box=True,
        hierarchical_namespaces=True,
    )

    source = ModwireMermaidFactory.standard().compile(diagram)
    assert "hideEmptyMembersBox: true" in source
    assert "classDiagram" in source
    assert 'namespace domain.policy["Domain policies"]' in source
    assert 'class UseCase~T~["Use Case"]' in source
    assert "+execute() Result" in source
    assert "UseCase ..> Policy : uses" in source
    assert 'link UseCase "https://example.com/use-case" "Open documentation"' in source


def test_class_diagram_covers_rich_mermaid_syntax():
    color = ModwireClassStyleProperty(name="fill", value="#f9f")
    diagram = ModwireClassDiagram(
        classes=(
            ModwireClass(
                id="Service-猫",
                label="Service 猫",
                members=(
                    ModwireClassAttribute(
                        name="repository",
                        type="Repository~Entity~",
                        visibility=ModwireVisibility.PRIVATE,
                        is_static=True,
                    ),
                    ModwireClassMethod(
                        name="load",
                        parameters=(),
                        return_type="Entity",
                        visibility=ModwireVisibility.PROTECTED,
                        classifiers=(ModwireMemberClassifier.ABSTRACT,),
                    ),
                ),
                annotations=("Service", "Abstract"),
                namespace="",
                generic_type="Entity",
                css_classes=("important",),
            ),
        ),
        relationships=(
            ModwireClassRelationship(
                source="Port",
                target="Service-猫",
                source_end=ModwireRelationshipEnd.LOLLIPOP,
                line=ModwireRelationshipLine.SOLID,
                target_end=ModwireRelationshipEnd.NONE,
                label="provides",
                source_cardinality="1",
                target_cardinality="0..n",
            ),
        ),
        direction=ModwireClassDiagramDirection.LEFT_RIGHT,
        comments=("complete class syntax",),
        notes=(ModwireClassNote(class_id="Service-猫", text="line1\\nline2"),),
        interactions=(
            ModwireClassInteraction(
                class_id="Service-猫",
                kind=ModwireClassInteractionKind.CALLBACK,
                reference="inspectService",
                tooltip="Inspect",
                syntax=ModwireClassInteractionSyntax.CLICK,
            ),
        ),
        namespaces=(),
        styles=(ModwireClassStyle(class_id="Service-猫", properties=(color,)),),
        style_definitions=(ModwireClassStyleDefinition(names=("important", "highlighted"), properties=(color,)),),
        hide_empty_members_box=False,
        hierarchical_namespaces=False,
    )

    source = ModwireMermaidFactory.standard().compile(diagram)

    assert "%% complete class syntax" in source
    assert "<<Service>>" in source
    assert "-Repository~Entity~ repository$" in source
    assert "#load() Entity*" in source
    assert 'Port "1" ()-- "0..n" Service-猫 : provides' in source
    assert 'note for Service-猫 "line1\\\\nline2"' in source
    assert 'click Service-猫 call inspectService() "Inspect"' in source
    assert "style Service-猫 fill:#f9f" in source
    assert "classDef important,highlighted fill:#f9f;" in source
    assert 'cssClass "Service-猫" important' in source


def test_file_tree_builds_safe_sorted_tree():
    source = ModwireMermaidFactory.standard().compile(
        ModwireFileTree(
            root=ModwireFileTreeNode(
                label="module",
                is_directory=True,
                description="Package root",
                icon="folder",
                css_classes=("highlight",),
                children=(
                    ModwireFileTreeNode(
                        label="application",
                        is_directory=True,
                        description="",
                        icon="",
                        css_classes=(),
                        children=(
                            ModwireFileTreeNode(
                                label="use_case.py",
                                is_directory=False,
                                description="Use cases",
                                icon="material-icon-theme:python",
                                css_classes=(),
                                children=(),
                            ),
                        ),
                    ),
                    ModwireFileTreeNode(
                        label="domain",
                        is_directory=True,
                        description="",
                        icon="",
                        css_classes=(),
                        children=(
                            ModwireFileTreeNode(
                                label="model.py",
                                is_directory=False,
                                description="",
                                icon="",
                                css_classes=(),
                                children=(),
                            ),
                            ModwireFileTreeNode(
                                label="policy.py",
                                is_directory=False,
                                description="",
                                icon="",
                                css_classes=(),
                                children=(),
                            ),
                        ),
                    ),
                ),
            ),
            comments=("project files",),
            row_indent=10,
            padding_x=5,
            padding_y=5,
            line_thickness=1,
            show_icons=True,
            default_icon_pack="material-icon-theme",
            filename_icons=(ModwireFileTreeIconMapping(pattern="README.md", icon="material-icon-theme:readme"),),
            extension_icons=(ModwireFileTreeIconMapping(pattern="py", icon="material-icon-theme:python"),),
            label_font_size="16px",
            label_color="black",
            line_color="black",
            icon_color="#546e7a",
            description_color="#6a9955",
            highlight_background="rgba(255,193,7,0.15)",
            highlight_stroke="#ffc107",
        )
    )

    assert "treeView-beta\n" in source
    assert source.index("application") < source.index("domain")
    assert "policy.py" in source
    assert '"module"/ icon(folder) :::highlight ## Package root' in source
    assert "icon(material-icon-theme:python) ## Use cases" in source
    assert '"py": "material-icon-theme:python"' in source


def test_file_tree_rejects_children_on_files():
    with pytest.raises(ValidationError, match="cannot contain children"):
        ModwireFileTreeNode(
            label="file.txt",
            is_directory=False,
            description="",
            icon="",
            css_classes=(),
            children=(
                ModwireFileTreeNode(
                    label="nested.txt",
                    is_directory=False,
                    description="",
                    icon="",
                    css_classes=(),
                    children=(),
                ),
            ),
        )


def test_base_diagram_rejects_empty_child_collections():
    with pytest.raises(ValidationError, match="root must be a directory"):
        ModwireFileTree(
            root=ModwireFileTreeNode(
                label="module.py",
                is_directory=False,
                description="",
                icon="",
                css_classes=(),
                children=(),
            ),
            comments=(),
            row_indent=10,
            padding_x=5,
            padding_y=5,
            line_thickness=1,
            show_icons=False,
            default_icon_pack="",
            filename_icons=(),
            extension_icons=(),
            label_font_size="16px",
            label_color="black",
            line_color="black",
            icon_color="#546e7a",
            description_color="#6a9955",
            highlight_background="rgba(255,193,7,0.15)",
            highlight_stroke="#ffc107",
        )


def test_mindmap_rejects_duplicate_sibling_children():
    with pytest.raises(ValidationError, match="children must be unique"):
        ModwireMindmap(
            root=ModwireMindmapNode(
                id="planning",
                label="Planning",
                shape=ModwireMindmapShape.SQUARE,
                text_format=ModwireMindmapTextFormat.PLAIN,
                icon_classes=(),
                css_classes=(),
                children=(
                    ModwireMindmapNode(
                        id="draft",
                        label="Draft",
                        shape=ModwireMindmapShape.SQUARE,
                        text_format=ModwireMindmapTextFormat.PLAIN,
                        icon_classes=(),
                        css_classes=(),
                        children=(),
                    ),
                    ModwireMindmapNode(
                        id="draft",
                        label="Draft again",
                        shape=ModwireMindmapShape.SQUARE,
                        text_format=ModwireMindmapTextFormat.PLAIN,
                        icon_classes=(),
                        css_classes=(),
                        children=(),
                    ),
                ),
            ),
            layout=ModwireMindmapLayout.DEFAULT,
        )


def test_mindmap_is_an_independent_fourth_compiler():
    diagram = ModwireMindmap(
        root=ModwireMindmapNode(
            id="planning",
            label="Planning",
            shape=ModwireMindmapShape.SQUARE,
            text_format=ModwireMindmapTextFormat.PLAIN,
            icon_classes=(),
            css_classes=(),
            children=(
                ModwireMindmapNode(
                    id="draft",
                    label="Draft",
                    shape=ModwireMindmapShape.ROUNDED_SQUARE,
                    text_format=ModwireMindmapTextFormat.PLAIN,
                    icon_classes=(),
                    css_classes=(),
                    children=(),
                ),
                ModwireMindmapNode(
                    id="epics",
                    label="Epics",
                    shape=ModwireMindmapShape.CIRCLE,
                    text_format=ModwireMindmapTextFormat.PLAIN,
                    icon_classes=(),
                    css_classes=(),
                    children=(),
                ),
            ),
        ),
        layout=ModwireMindmapLayout.DEFAULT,
    )

    source = ModwireMermaidFactory.standard().compile(diagram)

    assert source.startswith("mindmap\n")
    assert "Planning" in source
    assert "Draft" in source


def test_mindmap_covers_all_documented_shapes_icons_classes_markdown_and_layout():
    children = tuple(
        ModwireMindmapNode(
            id=identifier,
            label=label,
            shape=shape,
            text_format=text_format,
            icon_classes=icon_classes,
            css_classes=css_classes,
            children=(),
        )
        for identifier, label, shape, text_format, icon_classes, css_classes in (
            (
                "square",
                "**Square**\nUnicode 猫",
                ModwireMindmapShape.SQUARE,
                ModwireMindmapTextFormat.MARKDOWN,
                ("fa", "fa-book"),
                ("urgent", "large"),
            ),
            ("rounded", "Rounded", ModwireMindmapShape.ROUNDED_SQUARE, ModwireMindmapTextFormat.PLAIN, (), ()),
            ("bang", "Bang", ModwireMindmapShape.BANG, ModwireMindmapTextFormat.PLAIN, (), ()),
            ("cloud", "Cloud", ModwireMindmapShape.CLOUD, ModwireMindmapTextFormat.PLAIN, (), ()),
            ("hexagon", "Hexagon", ModwireMindmapShape.HEXAGON, ModwireMindmapTextFormat.PLAIN, (), ()),
            ("Default", "Default", ModwireMindmapShape.DEFAULT, ModwireMindmapTextFormat.PLAIN, (), ()),
        )
    )
    diagram = ModwireMindmap(
        root=ModwireMindmapNode(
            id="root",
            label="Mindmap",
            shape=ModwireMindmapShape.CIRCLE,
            text_format=ModwireMindmapTextFormat.PLAIN,
            icon_classes=(),
            css_classes=(),
            children=children,
        ),
        layout=ModwireMindmapLayout.TIDY_TREE,
    )

    source = ModwireMermaidFactory.standard().compile(diagram)

    assert "layout: tidy-tree" in source
    assert 'root(("Mindmap"))' in source
    assert 'square["`**Square**\\nUnicode 猫`"]' in source
    assert "::icon(fa fa-book)" in source
    assert ":::urgent large" in source
    assert 'rounded("Rounded")' in source
    assert 'bang))"Bang"((' in source
    assert 'cloud)"Cloud"(' in source
    assert 'hexagon{{"Hexagon"}}' in source
    assert "    Default\n" in source
