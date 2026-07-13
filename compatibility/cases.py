from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

from modwire_mermaid.architecture.diagram import (
    ModwireArchitectureDiagram,
    ModwireArchitectureEdge,
    ModwireArchitectureGroup,
    ModwireArchitectureJunction,
    ModwireArchitectureService,
    ModwireArchitectureSide,
)
from modwire_mermaid.class_diagram.diagram import (
    ModwireClass,
    ModwireClassAttribute,
    ModwireClassDiagram,
    ModwireClassInteraction,
    ModwireClassInteractionKind,
    ModwireClassInteractionSyntax,
    ModwireClassMethod,
    ModwireClassNamespace,
    ModwireClassNote,
    ModwireClassParameter,
    ModwireClassRelationship,
    ModwireClassStyle,
    ModwireClassStyleDefinition,
    ModwireClassStyleProperty,
    ModwireRelationshipEnd,
    ModwireRelationshipLine,
    ModwireVisibility,
)
from modwire_mermaid.contracts import ModwireDiagramDirection
from modwire_mermaid.diagrams import Diagram
from modwire_mermaid.event_modeling.diagram import (
    ModwireEventDataBlock,
    ModwireEventDataType,
    ModwireEventEntityType,
    ModwireEventModel,
    ModwireEventTimeframe,
)
from modwire_mermaid.file_tree.diagram import ModwireFileTree, ModwireFileTreeIconMapping, ModwireFileTreeNode
from modwire_mermaid.graph import (
    ModwireFlowchart,
    ModwireFlowchartAnimation,
    ModwireFlowchartCurve,
    ModwireFlowchartEdge,
    ModwireFlowchartEdgeEnd,
    ModwireFlowchartEdgeLine,
    ModwireFlowchartIconForm,
    ModwireFlowchartIconNode,
    ModwireFlowchartImageConstraint,
    ModwireFlowchartImageNode,
    ModwireFlowchartInteraction,
    ModwireFlowchartInteractionKind,
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
from modwire_mermaid.sequence.diagram import (
    ModwireSequenceActivation,
    ModwireSequenceActivationKind,
    ModwireSequenceArrow,
    ModwireSequenceBlock,
    ModwireSequenceBlockKind,
    ModwireSequenceBranch,
    ModwireSequenceDiagram,
    ModwireSequenceLink,
    ModwireSequenceMessage,
    ModwireSequenceNote,
    ModwireSequenceNotePosition,
    ModwireSequenceParticipant,
    ModwireSequenceParticipantKind,
    ModwireSequenceRect,
)
from modwire_mermaid.state.diagram import (
    ModwireState,
    ModwireStateDiagram,
    ModwireStateKind,
    ModwireStateNote,
    ModwireStateNotePosition,
    ModwireStateStyleAssignment,
    ModwireStateStyleDefinition,
    ModwireStateStyleProperty,
    ModwireStateTransition,
)
from modwire_mermaid.swimlane.diagram import ModwireSwimlane, ModwireSwimlaneDiagram
from modwire_mermaid.timeline.diagram import (
    ModwireTimeline,
    ModwireTimelineDirection,
    ModwireTimelinePeriod,
    ModwireTimelineSection,
)
from modwire_mermaid.user_journey.diagram import ModwireUserJourney, ModwireUserJourneySection, ModwireUserJourneyTask

Profile = Literal["minimal", "comprehensive", "focused"]
Factory = Callable[[], Diagram]
InvalidFactory = Callable[[], BaseModel]


@dataclass(frozen=True, slots=True)
class CorpusCase:
    id: str
    kind: str
    profile: Profile
    factory: Factory
    render_required: bool
    claims: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class InvalidCase:
    id: str
    factory: InvalidFactory
    error_type: str
    location: tuple[str | int, ...]


def architecture_minimal() -> Diagram:
    return ModwireArchitectureDiagram(services=(ModwireArchitectureService(id="api", label="API"),))


def architecture_comprehensive() -> Diagram:
    return ModwireArchitectureDiagram(
        title="Cloud topology",
        groups=(
            ModwireArchitectureGroup(id="cloud", icon="cloud", label="Cloud"),
            ModwireArchitectureGroup(id="apps", label="Applications", parent_id="cloud"),
        ),
        services=(
            ModwireArchitectureService(id="web", icon="server", label="Web", group_id="apps"),
            ModwireArchitectureService(id="db", icon="database", label="Database", group_id="cloud"),
        ),
        junctions=(ModwireArchitectureJunction(id="gateway", group_id="cloud"),),
        edges=(
            ModwireArchitectureEdge(
                source="web",
                source_side=ModwireArchitectureSide.RIGHT,
                target="gateway",
                target_side=ModwireArchitectureSide.LEFT,
            ),
            ModwireArchitectureEdge(
                source="gateway",
                source_side=ModwireArchitectureSide.BOTTOM,
                target="db",
                target_side=ModwireArchitectureSide.TOP,
                bidirectional=True,
            ),
        ),
    )


def class_minimal() -> Diagram:
    return ModwireClassDiagram(classes=(ModwireClass(id="User", label="User"),))


def class_comprehensive() -> Diagram:
    return ModwireClassDiagram(
        classes=(
            ModwireClass(
                id="User",
                label="User 猫",
                namespace="domain",
                annotations=("entity",),
                generic_type="T",
                css_classes=("important",),
                members=(
                    ModwireClassAttribute(name="id", type="UUID", visibility=ModwireVisibility.PRIVATE),
                    ModwireClassMethod(
                        name="rename",
                        parameters=(ModwireClassParameter(name="name", type="str"),),
                        return_type="None",
                    ),
                ),
            ),
            ModwireClass(id="Repository", label="Repository", namespace="domain"),
        ),
        namespaces=(ModwireClassNamespace(id="domain", label="Domain"),),
        relationships=(
            ModwireClassRelationship(
                source="User",
                target="Repository",
                line=ModwireRelationshipLine.DASHED,
                target_end=ModwireRelationshipEnd.ASSOCIATION_RIGHT,
                label="stored by",
                source_cardinality="1",
                target_cardinality="*",
            ),
        ),
        notes=(ModwireClassNote(class_id="User", text="Immutable\naggregate"),),
        interactions=(
            ModwireClassInteraction(
                class_id="User",
                kind=ModwireClassInteractionKind.LINK,
                reference="https://example.test/user",
                tooltip="Documentation",
                syntax=ModwireClassInteractionSyntax.ACTION,
            ),
        ),
        styles=(
            ModwireClassStyle(class_id="User", properties=(ModwireClassStyleProperty(name="fill", value="#eef"),)),
        ),
        style_definitions=(
            ModwireClassStyleDefinition(
                names=("important",), properties=(ModwireClassStyleProperty(name="stroke", value="#334"),)
            ),
        ),
        comments=("typed contract",),
        hide_empty_members_box=True,
        hierarchical_namespaces=True,
    )


def event_modeling_minimal() -> Diagram:
    return ModwireEventModel(
        timeframes=(ModwireEventTimeframe(id="created", entity_type=ModwireEventEntityType.EVENT, entity="Created"),)
    )


def event_modeling_comprehensive() -> Diagram:
    return ModwireEventModel(
        timeframes=(
            ModwireEventTimeframe(
                id="screen",
                entity_type=ModwireEventEntityType.UI,
                entity="Sales.Screen",
                data_type=ModwireEventDataType.JSON,
                data='"locale":"pl"',
                relations=("command",),
            ),
            ModwireEventTimeframe(
                id="command",
                entity_type=ModwireEventEntityType.COMMAND,
                entity="Sales.PlaceOrder",
                relations=("event",),
            ),
            ModwireEventTimeframe(
                id="event",
                entity_type=ModwireEventEntityType.EVENT,
                entity="Sales.OrderPlaced",
                is_reset=True,
                data_block_id="payload",
            ),
        ),
        data_blocks=(ModwireEventDataBlock(id="payload", data_type=ModwireEventDataType.JSON, data='"id":"42"'),),
    )


def file_tree_minimal() -> Diagram:
    return ModwireFileTree(root=ModwireFileTreeNode(label="project", is_directory=True))


def file_tree_comprehensive() -> Diagram:
    return ModwireFileTree(
        root=ModwireFileTreeNode(
            label="project",
            is_directory=True,
            icon="folder",
            css_classes=("root",),
            children=(
                ModwireFileTreeNode(
                    label="src",
                    is_directory=True,
                    children=(
                        ModwireFileTreeNode(
                            label="猫.py", is_directory=False, description="Unicode module", icon="python"
                        ),
                    ),
                ),
                ModwireFileTreeNode(label="README.md", is_directory=False, description="Guide"),
            ),
        ),
        comments=("deterministic tree",),
        default_icon_pack="fa",
        filename_icons=(ModwireFileTreeIconMapping(pattern="README.md", icon="fa:book"),),
        extension_icons=(ModwireFileTreeIconMapping(pattern="py", icon="fa:python"),),
        label_color="#223344",
        line_color="#778899",
    )


def flowchart_minimal() -> Diagram:
    return ModwireFlowchart(nodes=(ModwireFlowchartNode(id="start", label="Start"),))


def flowchart_comprehensive() -> Diagram:
    image = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciLz4="
    return ModwireFlowchart(
        nodes=(
            ModwireFlowchartNode(
                id="start",
                label="**Start**",
                shape=ModwireFlowchartShape.START,
                text_format=ModwireFlowchartTextFormat.MARKDOWN,
                css_classes=("primary",),
            ),
            ModwireFlowchartIconNode(id="icon", icon="fa:fa-user", label="User", form=ModwireFlowchartIconForm.CIRCLE),
            ModwireFlowchartImageNode(
                id="image",
                image_url=image,
                label="Image",
                width=80,
                height=60,
                constraint=ModwireFlowchartImageConstraint.ON,
            ),
            ModwireFlowchartNode(id="decision", label="Ready?", shape=ModwireFlowchartShape.DECISION),
        ),
        edges=(
            ModwireFlowchartEdge(id="e0", source="start", target="icon", label="go", minimum_length=2),
            ModwireFlowchartEdge(
                id="e1",
                source="icon",
                target="image",
                line=ModwireFlowchartEdgeLine.DOTTED,
                source_end=ModwireFlowchartEdgeEnd.CIRCLE,
                target_end=ModwireFlowchartEdgeEnd.ARROW,
                animation=ModwireFlowchartAnimation.FAST,
            ),
            ModwireFlowchartEdge(
                id="e2",
                source="image",
                target="decision",
                line=ModwireFlowchartEdgeLine.THICK,
                curve=ModwireFlowchartCurve.BASIS,
            ),
        ),
        subgraphs=(ModwireFlowchartSubgraph(id="process", label="Process", node_ids=("icon", "image")),),
        interactions=(
            ModwireFlowchartInteraction(
                node_id="start",
                kind=ModwireFlowchartInteractionKind.LINK,
                reference="https://example.test",
                tooltip="Open",
                link_target=ModwireFlowchartLinkTarget.BLANK,
            ),
        ),
        node_styles=(
            ModwireFlowchartNodeStyle(
                node_id="decision", properties=(ModwireFlowchartStyleProperty(name="fill", value="#ffd"),)
            ),
        ),
        link_styles=(
            ModwireFlowchartLinkStyle(
                edge_indexes=(0,), properties=(ModwireFlowchartStyleProperty(name="stroke", value="blue"),)
            ),
        ),
        style_definitions=(
            ModwireFlowchartStyleDefinition(
                names=("primary",), properties=(ModwireFlowchartStyleProperty(name="color", value="#111"),)
            ),
        ),
        comments=("icons images markdown interactions styles",),
    )


def mindmap_minimal() -> Diagram:
    return ModwireMindmap(root=ModwireMindmapNode(id="Root", label="Root"))


def mindmap_comprehensive() -> Diagram:
    children = tuple(
        ModwireMindmapNode(id=shape.name, label=shape.value, shape=shape)
        for shape in ModwireMindmapShape
        if shape is not ModwireMindmapShape.DEFAULT
    )
    markdown = ModwireMindmapNode(
        id="Markdown",
        label="**Unicode 猫**\nsecond line",
        shape=ModwireMindmapShape.SQUARE,
        text_format=ModwireMindmapTextFormat.MARKDOWN,
        icon_classes=("fa", "fa-book"),
        css_classes=("focus",),
    )
    return ModwireMindmap(
        root=ModwireMindmapNode(id="Root", label="Root", children=(*children, markdown)),
        layout=ModwireMindmapLayout.TIDY_TREE,
    )


def sequence_minimal() -> Diagram:
    return ModwireSequenceDiagram(
        participants=(
            ModwireSequenceParticipant(id="client", label="Client"),
            ModwireSequenceParticipant(id="api", label="API"),
        ),
        statements=(ModwireSequenceMessage(source="client", target="api", text="Request"),),
    )


def sequence_comprehensive() -> Diagram:
    participants = (
        ModwireSequenceParticipant(
            id="client",
            label="Client 猫",
            kind=ModwireSequenceParticipantKind.ACTOR,
            box="Users",
            box_color="rgb(240,240,240)",
        ),
        ModwireSequenceParticipant(id="api", label="API", box="System"),
        ModwireSequenceParticipant(
            id="docs",
            label="Documentation",
            links=(ModwireSequenceLink(label="docs", url="https://example.test/docs"),),
        ),
        ModwireSequenceParticipant(id="boundary", label="Boundary", kind=ModwireSequenceParticipantKind.BOUNDARY),
        ModwireSequenceParticipant(id="control", label="Control", kind=ModwireSequenceParticipantKind.CONTROL),
        ModwireSequenceParticipant(id="entity", label="Entity", kind=ModwireSequenceParticipantKind.ENTITY),
        ModwireSequenceParticipant(id="database", label="Database", kind=ModwireSequenceParticipantKind.DATABASE),
        ModwireSequenceParticipant(
            id="collections", label="Collections", kind=ModwireSequenceParticipantKind.COLLECTIONS
        ),
        ModwireSequenceParticipant(id="queue", label="Queue", kind=ModwireSequenceParticipantKind.QUEUE),
    )
    arrow_messages = tuple(
        ModwireSequenceMessage(source="client", target="api", text=arrow.name, arrow=arrow)
        for arrow in ModwireSequenceArrow
    )
    return ModwireSequenceDiagram(
        title="Protocol",
        participants=participants,
        autonumber=True,
        comments=("all arrows and blocks",),
        statements=(
            *arrow_messages,
            ModwireSequenceActivation(participant_id="api", kind=ModwireSequenceActivationKind.ACTIVATE),
            ModwireSequenceNote(
                participant_ids=("client", "api"), position=ModwireSequenceNotePosition.OVER, text="Shared note"
            ),
            ModwireSequenceRect(
                color="rgba(200,200,255,0.3)",
                statements=(
                    ModwireSequenceBlock(
                        kind=ModwireSequenceBlockKind.ALTERNATIVE,
                        label="Valid",
                        statements=(ModwireSequenceMessage(source="api", target="client", text="OK"),),
                        branches=(
                            ModwireSequenceBranch(
                                label="Invalid",
                                statements=(ModwireSequenceMessage(source="api", target="client", text="Error"),),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )


def state_minimal() -> Diagram:
    return ModwireStateDiagram(
        states=(ModwireState(id="Idle", label="Idle"),),
        transitions=(ModwireStateTransition(source="[*]", target="Idle"),),
    )


def state_comprehensive() -> Diagram:
    children = (
        ModwireState(id="Idle", label="Idle"),
        ModwireState(id="Choice", label="Choice", kind=ModwireStateKind.CHOICE),
        ModwireState(id="Fork", label="Fork", kind=ModwireStateKind.FORK),
        ModwireState(id="Join", label="Join", kind=ModwireStateKind.JOIN),
    )
    return ModwireStateDiagram(
        states=(
            ModwireState(
                id="Active",
                label="Active",
                children=children,
                transitions=(ModwireStateTransition(source="Idle", target="Choice", label="decide"),),
                concurrent_regions=(("Fork",), ("Join",)),
                direction=ModwireDiagramDirection.LEFT_RIGHT,
            ),
        ),
        transitions=(
            ModwireStateTransition(source="[*]", target="Active"),
            ModwireStateTransition(source="Active", target="[*]", label="finish"),
        ),
        comments=("composite state",),
        notes=(ModwireStateNote(state_id="Idle", position=ModwireStateNotePosition.RIGHT, text="Waiting"),),
        style_definitions=(
            ModwireStateStyleDefinition(
                name="active", properties=(ModwireStateStyleProperty(name="fill", value="#efe"),)
            ),
        ),
        style_assignments=(ModwireStateStyleAssignment(state_ids=("Active",), style_names=("active",)),),
        accessibility_title="Lifecycle",
        accessibility_description="Application lifecycle",
    )


def swimlane_minimal() -> Diagram:
    return ModwireSwimlaneDiagram(
        lanes=(ModwireSwimlane(id="team", label="Team", nodes=(ModwireFlowchartNode(id="task", label="Task"),)),)
    )


def swimlane_comprehensive() -> Diagram:
    image = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciLz4="
    return ModwireSwimlaneDiagram(
        lanes=(
            ModwireSwimlane(
                id="customer",
                label="Customer",
                nodes=(
                    ModwireFlowchartNode(
                        id="request",
                        label="**Request**",
                        shape=ModwireFlowchartShape.START,
                        text_format=ModwireFlowchartTextFormat.MARKDOWN,
                        css_classes=("primary",),
                    ),
                    ModwireFlowchartIconNode(id="person", icon="fa:fa-user", label="Person"),
                ),
            ),
            ModwireSwimlane(
                id="system",
                label="System",
                nodes=(
                    ModwireFlowchartImageNode(id="asset", image_url=image, label="Asset", width=64, height=64),
                    ModwireFlowchartNode(id="decision", label="Ready?", shape=ModwireFlowchartShape.DECISION),
                ),
            ),
        ),
        edges=(
            ModwireFlowchartEdge(id="s0", source="request", target="person", label="owns"),
            ModwireFlowchartEdge(id="s1", source="person", target="asset", line=ModwireFlowchartEdgeLine.DOTTED),
            ModwireFlowchartEdge(id="s2", source="asset", target="decision", line=ModwireFlowchartEdgeLine.THICK),
        ),
        interactions=(
            ModwireFlowchartInteraction(
                node_id="request",
                kind=ModwireFlowchartInteractionKind.LINK,
                reference="https://example.test/request",
                tooltip="Open request",
            ),
        ),
        node_styles=(
            ModwireFlowchartNodeStyle(
                node_id="decision", properties=(ModwireFlowchartStyleProperty(name="fill", value="#ffd"),)
            ),
        ),
        link_styles=(
            ModwireFlowchartLinkStyle(
                edge_indexes=(1,), properties=(ModwireFlowchartStyleProperty(name="stroke", value="blue"),)
            ),
        ),
        style_definitions=(
            ModwireFlowchartStyleDefinition(
                names=("primary",), properties=(ModwireFlowchartStyleProperty(name="color", value="#111"),)
            ),
        ),
        comments=("beta reuse proof",),
        accessibility_title="Ownership",
        accessibility_description="Cross-lane handoff",
    )


def timeline_minimal() -> Diagram:
    return ModwireTimeline(
        sections=(
            ModwireTimelineSection(name="2026", periods=(ModwireTimelinePeriod(name="Q1", events=("Release",)),)),
        )
    )


def timeline_comprehensive() -> Diagram:
    return ModwireTimeline(
        title="History 猫",
        direction=ModwireTimelineDirection.TOP_DOWN,
        disable_multicolor=True,
        sections=(
            ModwireTimelineSection(
                name="2025", periods=(ModwireTimelinePeriod(name="Q4", events=("Design", "Preview")),)
            ),
            ModwireTimelineSection(
                name="2026",
                periods=(
                    ModwireTimelinePeriod(name="Q1", events=("Release",)),
                    ModwireTimelinePeriod(name="Q2", events=("Docs", "Adoption")),
                ),
            ),
        ),
    )


def user_journey_minimal() -> Diagram:
    return ModwireUserJourney(
        title="Journey",
        sections=(ModwireUserJourneySection(name="Use", tasks=(ModwireUserJourneyTask(name="Start", score=3),)),),
    )


def user_journey_comprehensive() -> Diagram:
    return ModwireUserJourney(
        title="Customer journey 猫",
        sections=(
            ModwireUserJourneySection(
                name="Discover",
                tasks=tuple(
                    ModwireUserJourneyTask(name=f"Step {score}", score=score, actors=("Customer", "System"))
                    for score in range(1, 6)
                ),
            ),
            ModwireUserJourneySection(
                name="Adopt", tasks=(ModwireUserJourneyTask(name="Ship", score=5, actors=("Team",)),)
            ),
        ),
    )


CASES = (
    CorpusCase("architecture.minimal", "architecture", "minimal", architecture_minimal, False, ("services",)),
    CorpusCase(
        "architecture.comprehensive",
        "architecture",
        "comprehensive",
        architecture_comprehensive,
        True,
        ("groups", "junctions", "edges", "icons", "title"),
    ),
    CorpusCase("class.minimal", "class", "minimal", class_minimal, False, ("class",)),
    CorpusCase(
        "class.comprehensive",
        "class",
        "comprehensive",
        class_comprehensive,
        True,
        ("members", "namespaces", "relationships", "notes", "interactions", "styles", "config"),
    ),
    CorpusCase("event-modeling.minimal", "event-modeling", "minimal", event_modeling_minimal, False, ("entity-types",)),
    CorpusCase(
        "event-modeling.comprehensive",
        "event-modeling",
        "comprehensive",
        event_modeling_comprehensive,
        True,
        ("reset", "relations", "inline-data", "data-block", "namespaces"),
    ),
    CorpusCase("file-tree.minimal", "file-tree", "minimal", file_tree_minimal, False, ("syntax",)),
    CorpusCase(
        "file-tree.comprehensive",
        "file-tree",
        "comprehensive",
        file_tree_comprehensive,
        True,
        ("recursive", "icons", "classes", "config", "unicode"),
    ),
    CorpusCase("flowchart.minimal", "flowchart", "minimal", flowchart_minimal, False, ("nodes",)),
    CorpusCase(
        "flowchart.comprehensive",
        "flowchart",
        "comprehensive",
        flowchart_comprehensive,
        True,
        ("shapes", "icons", "images", "markdown", "edges", "subgraphs", "interactions", "styles"),
    ),
    CorpusCase("mindmap.minimal", "mindmap", "minimal", mindmap_minimal, False, ("syntax",)),
    CorpusCase(
        "mindmap.comprehensive",
        "mindmap",
        "comprehensive",
        mindmap_comprehensive,
        True,
        ("shapes", "markdown", "icons", "classes", "layout", "unicode"),
    ),
    CorpusCase("sequence.minimal", "sequence", "minimal", sequence_minimal, False, ("participants", "messages")),
    CorpusCase(
        "sequence.comprehensive",
        "sequence",
        "comprehensive",
        sequence_comprehensive,
        True,
        ("participant-kinds", "arrows", "activation", "notes", "links", "blocks", "autonumber"),
    ),
    CorpusCase("state.minimal", "state", "minimal", state_minimal, False, ("states", "transitions")),
    CorpusCase(
        "state.comprehensive",
        "state",
        "comprehensive",
        state_comprehensive,
        True,
        ("composite", "choice", "fork", "join", "concurrency", "notes", "styles", "accessibility"),
    ),
    CorpusCase("swimlane.minimal", "swimlane", "minimal", swimlane_minimal, True, ("lanes", "nodes")),
    CorpusCase(
        "swimlane.comprehensive",
        "swimlane",
        "comprehensive",
        swimlane_comprehensive,
        True,
        ("flowchart-reuse", "icons", "images", "markdown", "edges", "interactions", "styles", "accessibility"),
    ),
    CorpusCase("timeline.minimal", "timeline", "minimal", timeline_minimal, False, ("sections", "periods")),
    CorpusCase(
        "timeline.comprehensive",
        "timeline",
        "comprehensive",
        timeline_comprehensive,
        True,
        ("title", "directions", "events", "config", "unicode"),
    ),
    CorpusCase("user-journey.minimal", "user-journey", "minimal", user_journey_minimal, False, ("syntax",)),
    CorpusCase(
        "user-journey.comprehensive",
        "user-journey",
        "comprehensive",
        user_journey_comprehensive,
        True,
        ("sections", "scores", "actors", "unicode"),
    ),
    CorpusCase(
        "mindmap.focused-recursive-unicode",
        "mindmap",
        "focused",
        mindmap_comprehensive,
        True,
        ("recursive-depth", "multiline", "unicode"),
    ),
    CorpusCase(
        "swimlane.focused-flowchart-reuse",
        "swimlane",
        "focused",
        swimlane_comprehensive,
        True,
        ("beta", "flowchart-reuse"),
    ),
)


INVALID_CASES = (
    InvalidCase(
        "architecture.invalid-reference",
        lambda: ModwireArchitectureDiagram(services=(ModwireArchitectureService(id="api", group_id="missing"),)),
        "unknown_reference",
        ("services", 0, "group_id"),
    ),
    InvalidCase(
        "flowchart.invalid-reference",
        lambda: ModwireFlowchart(
            nodes=(ModwireFlowchartNode(id="known", label="Known"),),
            edges=(ModwireFlowchartEdge(source="known", target="missing"),),
        ),
        "unknown_reference",
        ("edges", 0, "target"),
    ),
    InvalidCase(
        "sequence.invalid-reference",
        lambda: ModwireSequenceDiagram(
            participants=(ModwireSequenceParticipant(id="known", label="Known"),),
            statements=(ModwireSequenceMessage(source="known", target="missing", text="Bad"),),
        ),
        "unknown_reference",
        ("statements", 0, "target"),
    ),
    InvalidCase("timeline.invalid-empty", lambda: ModwireTimeline(sections=()), "value_error", ()),
)
