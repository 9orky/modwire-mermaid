from modwire_mermaid.architecture.compiler import ModwireArchitectureCompiler
from modwire_mermaid.architecture.diagram import (
    ModwireArchitectureDiagram,
    ModwireArchitectureEdge,
    ModwireArchitectureGroup,
    ModwireArchitectureJunction,
    ModwireArchitectureService,
    ModwireArchitectureSide,
)
from modwire_mermaid.architecture.template import ModwireArchitectureTemplate
from modwire_mermaid.contracts import ModwireDiagramDirection
from modwire_mermaid.event_modeling.compiler import ModwireEventModelCompiler
from modwire_mermaid.event_modeling.diagram import (
    ModwireEventDataBlock,
    ModwireEventDataType,
    ModwireEventEntityType,
    ModwireEventModel,
    ModwireEventTimeframe,
)
from modwire_mermaid.event_modeling.template import ModwireEventModelTemplate
from modwire_mermaid.state.compiler import ModwireStateCompiler
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
from modwire_mermaid.state.template import ModwireStateTemplate
from modwire_mermaid.timeline.compiler import ModwireTimelineCompiler
from modwire_mermaid.timeline.diagram import (
    ModwireTimeline,
    ModwireTimelineDirection,
    ModwireTimelinePeriod,
    ModwireTimelineSection,
)
from modwire_mermaid.timeline.template import ModwireTimelineTemplate
from modwire_mermaid.user_journey.compiler import ModwireUserJourneyCompiler
from modwire_mermaid.user_journey.diagram import (
    ModwireUserJourney,
    ModwireUserJourneySection,
    ModwireUserJourneyTask,
)
from modwire_mermaid.user_journey.template import ModwireUserJourneyTemplate


def test_architecture_supports_junctions_and_group_edges():
    diagram = ModwireArchitectureDiagram(
        groups=(ModwireArchitectureGroup(id="cloud", icon="cloud", label="Cloud"),),
        services=(ModwireArchitectureService(id="api", icon="server", label="API", group_id="cloud"),),
        junctions=(ModwireArchitectureJunction(id="gateway", group_id="cloud"),),
        edges=(
            ModwireArchitectureEdge(
                source="api",
                source_side=ModwireArchitectureSide.RIGHT,
                source_group_edge=True,
                target="gateway",
                target_side=ModwireArchitectureSide.LEFT,
                target_group_edge=False,
                bidirectional=False,
            ),
        ),
        title="Platform",
    )

    source = ModwireArchitectureCompiler(ModwireArchitectureTemplate.standard()).compile(diagram)

    assert "junction gateway in cloud" in source
    assert "api{group}:R --> gateway:L" in source


def test_event_modeling_supports_reset_relations_and_typed_data_blocks():
    diagram = ModwireEventModel(
        timeframes=(
            ModwireEventTimeframe(
                id="01",
                entity_type=ModwireEventEntityType.EVENT,
                entity="CartCreated",
                is_reset=True,
                data_type=ModwireEventDataType.NONE,
                data="",
                data_block_id="",
                relations=(),
            ),
            ModwireEventTimeframe(
                id="02",
                entity_type=ModwireEventEntityType.READ_MODEL,
                entity="CartUI",
                is_reset=False,
                data_type=ModwireEventDataType.NONE,
                data="",
                data_block_id="CartData",
                relations=("01",),
            ),
        ),
        data_blocks=(ModwireEventDataBlock(id="CartData", data_type=ModwireEventDataType.JSON, data='{"id": 1}'),),
    )

    source = ModwireEventModelCompiler(ModwireEventModelTemplate.standard()).compile(diagram)

    assert "rf 01 evt CartCreated" in source
    assert "tf 02 rmo CartUI [[CartData]] ->> 01" in source
    assert "data CartData `json`{" in source


def test_state_supports_composites_notes_accessibility_and_styles():
    child = ModwireState(
        id="Idle",
        label="Idle",
        kind=ModwireStateKind.SIMPLE,
        children=(),
        transitions=(),
        concurrent_regions=(),
        direction="",
    )
    diagram = ModwireStateDiagram(
        states=(
            ModwireState(
                id="Active",
                label="Active",
                kind=ModwireStateKind.SIMPLE,
                children=(child,),
                transitions=(ModwireStateTransition(source="[*]", target="Idle", label="start"),),
                concurrent_regions=(),
                direction=ModwireDiagramDirection.LEFT_RIGHT,
            ),
        ),
        transitions=(ModwireStateTransition(source="[*]", target="Active", label=""),),
        direction=ModwireDiagramDirection.LEFT_RIGHT,
        comments=(),
        notes=(ModwireStateNote(state_id="Idle", position=ModwireStateNotePosition.RIGHT, text="Waiting"),),
        style_definitions=(
            ModwireStateStyleDefinition(
                name="quiet",
                properties=(ModwireStateStyleProperty(name="fill", value="white"),),
            ),
        ),
        style_assignments=(ModwireStateStyleAssignment(state_ids=("Idle",), style_names=("quiet",)),),
        accessibility_title="Lifecycle",
        accessibility_description="Application lifecycle",
    )

    source = ModwireStateCompiler(ModwireStateTemplate.standard()).compile(diagram)

    assert 'state "Active" as Active {' in source
    assert "note right of Idle : Waiting" in source
    assert "classDef quiet fill:white;" in source


def test_timeline_compiles_sections_direction_and_configuration():
    diagram = ModwireTimeline(
        title="Releases",
        sections=(
            ModwireTimelineSection(
                name="2026",
                periods=(ModwireTimelinePeriod(name="Q1", events=("Beta", "Launch")),),
            ),
        ),
        direction=ModwireTimelineDirection.TOP_DOWN,
        disable_multicolor=True,
    )

    source = ModwireTimelineCompiler(ModwireTimelineTemplate.standard()).compile(diagram)

    assert "disableMulticolor: true" in source
    assert "timeline TD" in source
    assert "Q1 : Beta : Launch" in source


def test_user_journey_compiles_sections_scores_and_actors():
    diagram = ModwireUserJourney(
        title="Checkout",
        sections=(
            ModwireUserJourneySection(
                name="Payment",
                tasks=(ModwireUserJourneyTask(name="Pay", score=4, actors=("Customer", "Gateway")),),
            ),
        ),
    )

    source = ModwireUserJourneyCompiler(ModwireUserJourneyTemplate.standard()).compile(diagram)

    assert "section Payment" in source
    assert "Pay: 4: Customer, Gateway" in source
