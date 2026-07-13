from dataclasses import dataclass
from typing import Literal

import pytest

from modwire_mermaid.contracts import (
    CompilerRegistrationError,
    DiagramCompilationError,
    DuplicateCompilerError,
    ModwireBaseDiagram,
    UnsupportedDiagramError,
)
from modwire_mermaid.diagrams import DiagramAdapter
from modwire_mermaid.facade import ModwireMermaid
from modwire_mermaid.registry import CompilerRegistry
from modwire_mermaid.timeline.diagram import ModwireTimeline, ModwireTimelinePeriod, ModwireTimelineSection


class ExtensionDiagram(ModwireBaseDiagram):
    kind: Literal["extension"] = "extension"
    label: str


class ExtensionCompiler:
    diagram_type = ExtensionDiagram

    def compile(self, diagram: ExtensionDiagram) -> str:
        return f"extension {diagram.label}\n"


class ReplacementCompiler:
    diagram_type = ExtensionDiagram

    def compile(self, diagram: ExtensionDiagram) -> str:
        return f"replacement {diagram.label}\n"


class BrokenCompiler:
    diagram_type = ExtensionDiagram

    def compile(self, diagram: ExtensionDiagram) -> str:
        raise RuntimeError(diagram.label)


@dataclass(frozen=True)
class StructuralDiagram:
    label: str
    kind: str = "structural"


class StructuralCompiler:
    diagram_type = StructuralDiagram

    def compile(self, diagram: StructuralDiagram) -> str:
        return f"structural {diagram.label}\n"


def test_external_diagram_uses_the_same_immutable_registry_contract():
    empty = CompilerRegistry.empty()
    registered = empty.with_compiler(ExtensionCompiler())

    assert empty.registered_types == ()
    assert ModwireMermaid(registered).compile(ExtensionDiagram(label="demo")) == "extension demo\n"
    assert ModwireMermaid(registered.replace(ReplacementCompiler())).compile(ExtensionDiagram(label="demo")) == (
        "replacement demo\n"
    )
    assert registered.without(ExtensionDiagram).registered_types == ()


def test_non_pydantic_structural_diagram_registers_and_compiles():
    registry = CompilerRegistry.empty().with_compiler(StructuralCompiler())

    assert ModwireMermaid(registry).compile(StructuralDiagram(label="demo")) == "structural demo\n"


@pytest.mark.parametrize("compiler", [object(), type("MissingType", (), {"compile": lambda self, diagram: ""})()])
def test_invalid_runtime_compilers_use_registration_error_taxonomy(compiler):
    with pytest.raises(CompilerRegistrationError):
        CompilerRegistry.empty().with_compiler(compiler)


def test_registry_conflicts_and_missing_operations_are_explicit():
    registry = CompilerRegistry.empty().with_compiler(ExtensionCompiler())
    with pytest.raises(DuplicateCompilerError):
        registry.with_compiler(ReplacementCompiler())
    with pytest.raises(DuplicateCompilerError):
        registry.merge(CompilerRegistry.empty().with_compiler(ReplacementCompiler()))
    with pytest.raises(CompilerRegistrationError):
        CompilerRegistry.empty().replace(ReplacementCompiler())
    with pytest.raises(UnsupportedDiagramError):
        ModwireMermaid(CompilerRegistry.empty()).compile(ExtensionDiagram(label="demo"))


def test_compiler_failures_preserve_context_and_cause():
    mermaid = ModwireMermaid(CompilerRegistry.empty().with_compiler(BrokenCompiler()))
    with pytest.raises(DiagramCompilationError) as captured:
        mermaid.compile(ExtensionDiagram(label="demo"))
    assert captured.value.diagram_kind == "extension"
    assert captured.value.compiler_type is BrokenCompiler
    assert isinstance(captured.value.__cause__, RuntimeError)


def test_diagrams_have_stable_discriminants_round_trip_and_concise_defaults():
    diagram = ModwireTimeline(
        sections=(ModwireTimelineSection(name="2026", periods=(ModwireTimelinePeriod(name="Q1", events=("Go",)),)),)
    )
    dumped = diagram.model_dump(mode="json")
    assert dumped["kind"] == "timeline"
    assert ModwireTimeline.model_validate_json(diagram.model_dump_json()) == diagram
    assert DiagramAdapter.validate_json(DiagramAdapter.dump_json(diagram)) == diagram
    schema = DiagramAdapter.json_schema()
    assert schema["discriminator"]["propertyName"] == "kind"
    assert diagram.title == "" and diagram.disable_multicolor is False
