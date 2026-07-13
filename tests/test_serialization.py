import pytest

from modwire_mermaid.architecture.diagram import ModwireArchitectureDiagram, ModwireArchitectureService
from modwire_mermaid.class_diagram.diagram import (
    ModwireClass,
    ModwireClassDiagram,
    ModwireClassMethod,
)
from modwire_mermaid.diagrams import DiagramAdapter
from modwire_mermaid.event_modeling.diagram import (
    ModwireEventEntityType,
    ModwireEventModel,
    ModwireEventTimeframe,
)
from modwire_mermaid.file_tree.diagram import ModwireFileTree, ModwireFileTreeNode
from modwire_mermaid.graph import (
    ModwireFlowchart,
    ModwireFlowchartNode,
    ModwireFlowchartSubgraph,
)
from modwire_mermaid.mindmap.diagram import ModwireMindmap, ModwireMindmapNode
from modwire_mermaid.sequence.diagram import (
    ModwireSequenceBlock,
    ModwireSequenceBlockKind,
    ModwireSequenceDiagram,
    ModwireSequenceMessage,
    ModwireSequenceParticipant,
    ModwireSequenceRect,
)
from modwire_mermaid.state.diagram import ModwireState, ModwireStateDiagram, ModwireStateTransition
from modwire_mermaid.swimlane.diagram import ModwireSwimlane, ModwireSwimlaneDiagram
from modwire_mermaid.timeline.diagram import ModwireTimeline, ModwireTimelinePeriod, ModwireTimelineSection
from modwire_mermaid.user_journey.diagram import ModwireUserJourney, ModwireUserJourneySection, ModwireUserJourneyTask

ROOT_DIAGRAMS = (
    ModwireArchitectureDiagram(services=(ModwireArchitectureService(id="service"),)),
    ModwireClassDiagram(classes=(ModwireClass(id="Class", label="Class"),)),
    ModwireEventModel(timeframes=(ModwireEventTimeframe(id="event", entity_type=ModwireEventEntityType.EVENT),)),
    ModwireFileTree(root=ModwireFileTreeNode(label="root", is_directory=True)),
    ModwireFlowchart(nodes=(ModwireFlowchartNode(id="node", label="Node"),)),
    ModwireMindmap(root=ModwireMindmapNode(id="Root", label="Root")),
    ModwireSequenceDiagram(participants=(ModwireSequenceParticipant(id="actor", label="Actor"),)),
    ModwireStateDiagram(states=(ModwireState(id="State", label="State"),)),
    ModwireSwimlaneDiagram(
        lanes=(
            ModwireSwimlane(
                id="lane",
                label="Lane",
                nodes=(ModwireFlowchartNode(id="node", label="Node"),),
            ),
        )
    ),
    ModwireTimeline(
        sections=(
            ModwireTimelineSection(name="2026", periods=(ModwireTimelinePeriod(name="Q1", events=("Release",)),)),
        )
    ),
    ModwireUserJourney(
        title="Journey",
        sections=(ModwireUserJourneySection(name="Use", tasks=(ModwireUserJourneyTask(name="Task", score=5),)),),
    ),
)


@pytest.mark.parametrize("diagram", ROOT_DIAGRAMS, ids=lambda diagram: diagram.kind)
def test_all_bundled_root_diagrams_have_deterministic_adapter_round_trips(diagram):
    encoded = DiagramAdapter.dump_json(diagram)

    assert DiagramAdapter.dump_json(DiagramAdapter.validate_json(encoded)) == encoded
    assert DiagramAdapter.validate_json(encoded) == diagram


@pytest.mark.parametrize(
    "diagram",
    [
        ModwireClassDiagram(
            classes=(
                ModwireClass(
                    id="Class",
                    label="Class",
                    members=(ModwireClassMethod(name="run", return_type="Result"),),
                ),
            )
        ),
        ModwireFileTree(
            root=ModwireFileTreeNode(
                label="root",
                is_directory=True,
                children=(ModwireFileTreeNode(label="file.py", is_directory=False),),
            )
        ),
        ModwireFlowchart(
            nodes=(ModwireFlowchartNode(id="node", label="Node"),),
            subgraphs=(
                ModwireFlowchartSubgraph(
                    id="outer",
                    children=(ModwireFlowchartSubgraph(id="inner", node_ids=("node",)),),
                ),
            ),
        ),
        ModwireMindmap(
            root=ModwireMindmapNode(id="Root", label="Root", children=(ModwireMindmapNode(id="Child", label="Child"),))
        ),
        ModwireSequenceDiagram(
            participants=(
                ModwireSequenceParticipant(id="one", label="One"),
                ModwireSequenceParticipant(id="two", label="Two"),
            ),
            statements=(
                ModwireSequenceBlock(
                    kind=ModwireSequenceBlockKind.LOOP,
                    label="Retry",
                    statements=(
                        ModwireSequenceRect(
                            color="red",
                            statements=(ModwireSequenceMessage(source="one", target="two", text="Run"),),
                        ),
                    ),
                ),
            ),
        ),
        ModwireStateDiagram(
            states=(
                ModwireState(
                    id="Parent",
                    label="Parent",
                    children=(ModwireState(id="Child", label="Child"),),
                    transitions=(ModwireStateTransition(source="[*]", target="Child"),),
                ),
            )
        ),
    ],
    ids=("class-member", "file-tree", "flow-subgraph", "mindmap", "sequence-statements", "state"),
)
def test_recursive_and_sum_type_variants_round_trip_without_shape_guessing(diagram):
    encoded = DiagramAdapter.dump_json(diagram)

    assert DiagramAdapter.validate_json(encoded) == diagram
    assert DiagramAdapter.dump_json(DiagramAdapter.validate_json(encoded)) == encoded
