from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

from .contracts import MermaidDiagram

DiagramT = TypeVar("DiagramT", bound=MermaidDiagram)


@runtime_checkable
class DiagramCompiler(Protocol[DiagramT]):
    """Compile one exact diagram type into deterministic Mermaid source."""

    @property
    def diagram_type(self) -> type[DiagramT]: ...

    def compile(self, diagram: DiagramT) -> str: ...
