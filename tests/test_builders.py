from dataclasses import FrozenInstanceError

import pytest
from pydantic import ValidationError

from modwire_mermaid import DiagramBuildError
from modwire_mermaid.timeline.diagram import (
    ModwireTimelineBuilder,
)


def test_timeline_builder_progressively_creates_a_valid_frozen_contract():
    diagram = (
        ModwireTimelineBuilder.create("Release history")
        .section("2026")
        .period("Q1", "Private beta")
        .period("Q2", "Public release", "Documentation")
        .build()
    )

    assert diagram.sections[0].periods[1].events == ("Public release", "Documentation")
    with pytest.raises(ValidationError, match="frozen"):
        diagram.title = "Changed"


def test_timeline_builder_requires_context_before_enrichment():
    with pytest.raises(DiagramBuildError, match="section"):
        ModwireTimelineBuilder.create("Release history").period("Q1", "Private beta")


def test_timeline_builder_is_frozen_and_fluent_operations_return_new_instances():
    original = ModwireTimelineBuilder.create("Release history")
    with_section = original.section("2026")

    assert with_section is not original
    with pytest.raises(DiagramBuildError, match="section"):
        original.period("Q1", "Private beta")
    with pytest.raises(FrozenInstanceError):
        original._title = "Changed"


def test_timeline_builder_delegates_final_contract_validation_to_pydantic():
    builder = ModwireTimelineBuilder.create("Release\nsequenceDiagram").section("2026").period("Q1", "Release")

    with pytest.raises(ValidationError) as captured:
        builder.build()

    assert captured.value.errors()[0]["loc"] == ("title",)
