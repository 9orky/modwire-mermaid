from modwire_mermaid.compiler import DiagramCompiler
from modwire_mermaid.contracts import ModwireDiagramDirection
from modwire_mermaid.flowchart.diagram import (
    ModwireFlowchartAnimation,
    ModwireFlowchartCurve,
    ModwireFlowchartEdge,
    ModwireFlowchartEdgeEnd,
    ModwireFlowchartEdgeLine,
    ModwireFlowchartNode,
    ModwireFlowchartShape,
    ModwireFlowchartTextFormat,
)
from modwire_mermaid.sequence.compiler import ModwireSequenceCompiler
from modwire_mermaid.sequence.diagram import (
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
)
from modwire_mermaid.sequence.template import ModwireSequenceTemplate
from modwire_mermaid.swimlane.compiler import ModwireSwimlaneCompiler
from modwire_mermaid.swimlane.diagram import ModwireSwimlane, ModwireSwimlaneDiagram
from modwire_mermaid.swimlane.template import ModwireSwimlaneTemplate


def test_sequence_supports_links_notes_and_control_blocks():
    message = ModwireSequenceMessage(
        source="client",
        target="api",
        text="Request",
        arrow=ModwireSequenceArrow.SOLID,
        activate_target=True,
        deactivate_target=False,
        central_source=False,
        central_target=False,
    )
    diagram = ModwireSequenceDiagram(
        participants=(
            ModwireSequenceParticipant(
                id="client",
                label="Client",
                kind=ModwireSequenceParticipantKind.ACTOR,
                links=(),
                box="Users",
                box_color="rgb(240,240,240)",
            ),
            ModwireSequenceParticipant(
                id="api",
                label="API",
                kind=ModwireSequenceParticipantKind.PARTICIPANT,
                links=(ModwireSequenceLink(label="Docs", url="https://example.test/docs"),),
                box="Services",
                box_color="",
            ),
        ),
        statements=(
            ModwireSequenceNote(
                participant_ids=("client", "api"),
                position=ModwireSequenceNotePosition.OVER,
                text="Interaction",
            ),
            ModwireSequenceBlock(
                kind=ModwireSequenceBlockKind.ALTERNATIVE,
                label="valid",
                statements=(message,),
                branches=(ModwireSequenceBranch(label="invalid", statements=()),),
            ),
        ),
        autonumber=True,
        title="Request flow",
        comments=(),
    )

    source = ModwireSequenceCompiler(ModwireSequenceTemplate.standard()).compile(diagram)

    assert 'links api: { "Docs": "https://example.test/docs" }' in source
    assert "Note over client,api: Interaction" in source
    assert "alt valid" in source and "else invalid" in source


def test_swimlane_reuses_full_flowchart_node_and_edge_rendering():
    nodes = (
        ModwireFlowchartNode(
            id="start",
            label="Start",
            shape=ModwireFlowchartShape.START,
            text_format=ModwireFlowchartTextFormat.PLAIN,
            css_classes=(),
        ),
        ModwireFlowchartNode(
            id="decision",
            label="**Ready?**",
            shape=ModwireFlowchartShape.DECISION,
            text_format=ModwireFlowchartTextFormat.MARKDOWN,
            css_classes=(),
        ),
    )
    edge = ModwireFlowchartEdge(
        id="",
        source="start",
        target="decision",
        label="continue",
        text_format=ModwireFlowchartTextFormat.PLAIN,
        line=ModwireFlowchartEdgeLine.THICK,
        source_end=ModwireFlowchartEdgeEnd.NONE,
        target_end=ModwireFlowchartEdgeEnd.ARROW,
        minimum_length=2,
        animation=ModwireFlowchartAnimation.NONE,
        curve=ModwireFlowchartCurve.DEFAULT,
        css_classes=(),
    )
    diagram = ModwireSwimlaneDiagram(
        lanes=(ModwireSwimlane(id="team", label="Team", nodes=nodes),),
        edges=(edge,),
        direction=ModwireDiagramDirection.LEFT_RIGHT,
        accessibility_title="Process",
        accessibility_description="Team process",
        interactions=(),
        node_styles=(),
        link_styles=(),
        style_definitions=(),
        comments=(),
    )

    source = ModwireSwimlaneCompiler(ModwireSwimlaneTemplate.standard()).compile(diagram)

    assert 'start@{ shape: circle, label: "Start" }' in source
    assert 'decision@{ shape: diam, label: "`**Ready?**`" }' in source
    assert 'start ===>|"continue"| decision' in source
    assert isinstance(ModwireSwimlaneCompiler(ModwireSwimlaneTemplate.standard()), DiagramCompiler)
