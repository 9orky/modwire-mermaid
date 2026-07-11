from __future__ import annotations

from abc import ABC, abstractmethod
from typing import cast

from .contracts import ModwireBaseDiagram


class DiagramCompiler[DiagramT: ModwireBaseDiagram](ABC):
    @property
    @abstractmethod
    def diagram_type(self) -> type[DiagramT]:
        raise NotImplementedError

    @abstractmethod
    def compile(self, diagram: DiagramT) -> str:
        raise NotImplementedError

    def compile_diagram(self, diagram: ModwireBaseDiagram) -> str:
        if not isinstance(diagram, self.diagram_type):
            raise TypeError(f"Expected {self.diagram_type.__name__}, got {type(diagram).__name__}")
        return self.compile(cast(DiagramT, diagram))
