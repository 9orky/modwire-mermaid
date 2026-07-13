from importlib import import_module

import pytest
from pydantic import ValidationError

from modwire_mermaid.architecture.diagram import (
    ModwireArchitectureDiagram,
    ModwireArchitectureGroup,
    ModwireArchitectureJunction,
    ModwireArchitectureService,
)
from modwire_mermaid.sequence.diagram import ModwireSequenceDiagram
from modwire_mermaid.state.diagram import ModwireStateDiagram
from modwire_mermaid.swimlane.diagram import ModwireSwimlaneDiagram
from modwire_mermaid.timeline.diagram import ModwireTimeline


@pytest.mark.parametrize(
    ("package", "forbidden_names"),
    [
        ("architecture", ("ModwireArchitectureDiagram", "ModwireArchitectureCompiler")),
        ("class_diagram", ("ModwireClassDiagram", "ModwireClassDiagramCompiler")),
        ("flowchart", ("ModwireFlowchart", "ModwireFlowchartCompiler")),
        ("sequence", ("ModwireSequenceDiagram", "ModwireSequenceCompiler")),
        ("state", ("ModwireStateDiagram", "ModwireStateCompiler")),
        ("swimlane", ("ModwireSwimlaneDiagram", "ModwireSwimlaneCompiler")),
        ("timeline", ("ModwireTimeline", "ModwireTimelineCompiler")),
    ],
)
def test_feature_packages_do_not_publish_convenience_barrels(package, forbidden_names):
    public_package = import_module(f"modwire_mermaid.{package}")

    assert all(not hasattr(public_package, name) for name in forbidden_names)


@pytest.mark.parametrize(
    ("model", "payload", "field"),
    [
        (ModwireArchitectureGroup, {"id": "group", "icon": None}, "icon"),
        (ModwireArchitectureGroup, {"id": "group", "label": None}, "label"),
        (ModwireArchitectureGroup, {"id": "group", "parent_id": None}, "parent_id"),
        (ModwireArchitectureService, {"id": "service", "icon": None}, "icon"),
        (ModwireArchitectureService, {"id": "service", "label": None}, "label"),
        (ModwireArchitectureService, {"id": "service", "group_id": None}, "group_id"),
        (ModwireArchitectureJunction, {"id": "junction", "group_id": None}, "group_id"),
        (ModwireArchitectureDiagram, {"services": (), "title": None}, "title"),
        (ModwireSequenceDiagram, {"participants": (), "title": None}, "title"),
        (ModwireStateDiagram, {"states": (), "accessibility_title": None}, "accessibility_title"),
        (
            ModwireStateDiagram,
            {"states": (), "accessibility_description": None},
            "accessibility_description",
        ),
        (ModwireSwimlaneDiagram, {"lanes": (), "accessibility_title": None}, "accessibility_title"),
        (
            ModwireSwimlaneDiagram,
            {"lanes": (), "accessibility_description": None},
            "accessibility_description",
        ),
        (ModwireTimeline, {"sections": (), "title": None}, "title"),
    ],
)
def test_public_models_reject_nullish_escape_hatches(model, payload, field):
    with pytest.raises(ValidationError) as captured:
        model.model_validate(payload)

    assert any(error["loc"] == (field,) for error in captured.value.errors())


def test_public_models_reject_undocumented_fields():
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ModwireArchitectureService(id="service", private_test_hook=True)


def test_architecture_references_are_empty_or_valid_identifiers():
    assert ModwireArchitectureService(id="service").group_id == ""
    with pytest.raises(ValidationError, match="String should match pattern"):
        ModwireArchitectureService(id="service", group_id="not a reference")
