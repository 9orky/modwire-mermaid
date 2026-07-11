from abc import ABC, abstractmethod
from collections.abc import Iterable

from .compiler import DiagramCompiler
from .contracts import ModwireBaseDiagram


class DiagramCompilerRegistry(ABC):
    @abstractmethod
    def compiler_for(self, diagram: ModwireBaseDiagram) -> DiagramCompiler:
        raise NotImplementedError


class CompilerRegistry(DiagramCompilerRegistry):
    def __init__(self, compilers: Iterable[DiagramCompiler]):
        items = tuple(compilers)
        diagram_types = tuple(compiler.diagram_type for compiler in items)
        if len(diagram_types) != len(set(diagram_types)):
            raise ValueError("Compiler registry requires one compiler per diagram type")
        self._compilers = dict(zip(diagram_types, items, strict=True))

    def compiler_for(self, diagram: ModwireBaseDiagram) -> DiagramCompiler:
        try:
            return self._compilers[type(diagram)]
        except KeyError as error:
            raise TypeError(f"No compiler registered for {type(diagram).__name__}") from error
