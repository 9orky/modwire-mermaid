import pytest
from pydantic import ValidationError

from modwire_mermaid import ModwireMermaidFactory
from modwire_mermaid.architecture.diagram import ModwireArchitectureDiagram, ModwireArchitectureService
from modwire_mermaid.class_diagram.diagram import ModwireClass, ModwireClassDiagram, ModwireClassNote
from modwire_mermaid.graph import (
    ModwireFlowchart,
    ModwireFlowchartInteraction,
    ModwireFlowchartInteractionKind,
    ModwireFlowchartNode,
    ModwireFlowchartStyleProperty,
)
from modwire_mermaid.sequence.diagram import ModwireSequenceLink
from modwire_mermaid.timeline.diagram import ModwireTimeline, ModwireTimelinePeriod, ModwireTimelineSection


def test_architecture_label_cannot_inject_a_statement_with_a_newline():
    with pytest.raises(ValidationError) as captured:
        ModwireArchitectureService(id="api", label="API\n  service injected")

    assert captured.value.errors()[0]["loc"] == ("label",)
    assert captured.value.errors()[0]["type"] == "string_pattern_mismatch"


def test_raw_architecture_label_delimiters_are_contextually_escaped():
    diagram = ModwireArchitectureDiagram(
        services=(ModwireArchitectureService(id="api", label="API]; service injected["),)
    )

    source = ModwireMermaidFactory.standard().compile(diagram)

    assert "API&#93&#59; service injected&#91;" not in source
    assert "API&#93;&#59; service injected&#91;" in source
    assert source.endswith("\n") and not source.endswith("\n\n")


@pytest.mark.parametrize(
    ("factory", "field"),
    [
        (
            lambda: ModwireTimeline(
                title="Release\nsequenceDiagram",
                sections=(
                    ModwireTimelineSection(name="2026", periods=(ModwireTimelinePeriod(name="Q1", events=("Go",)),)),
                ),
            ),
            "title",
        ),
        (
            lambda: ModwireFlowchart(
                nodes=(ModwireFlowchartNode(id="node", label="Node"),), comments=("safe\nflowchart LR",)
            ),
            "comments",
        ),
        (lambda: ModwireFlowchartStyleProperty(name="fill", value="red; class injected"), "value"),
        (lambda: ModwireSequenceLink(label="docs", url="https://example.test\nsequenceDiagram"), "url"),
    ],
)
def test_statement_breaks_are_rejected_at_title_comment_style_and_url_fields(factory, field):
    with pytest.raises(ValidationError) as captured:
        factory()

    assert captured.value.errors()[0]["loc"][0] == field


def test_quoted_multiline_text_is_escaped_without_creating_a_source_line():
    diagram = ModwireClassDiagram(
        classes=(ModwireClass(id="Service", label="Service"),),
        notes=(ModwireClassNote(class_id="Service", text="first\nsecond"),),
    )

    source = ModwireMermaidFactory.standard().compile(diagram)

    assert 'note for Service "first\\nsecond"' in source
    assert "\nsecond" not in source


def test_callback_context_rejects_statement_syntax():
    with pytest.raises(ValidationError) as captured:
        ModwireFlowchartInteraction(
            node_id="node",
            kind=ModwireFlowchartInteractionKind.CALLBACK,
            reference="callback; flowchart LR",
        )

    assert captured.value.errors()[0]["loc"] == ("reference",)
    assert captured.value.errors()[0]["type"] == "invalid_interaction_reference"
