from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Protocol, cast

from .compiler import DiagramCompiler
from .contracts import (
    CompilerRegistrationError,
    DiagramCompilationError,
    DuplicateCompilerError,
    MermaidDiagram,
    UnsupportedDiagramError,
)


class _ErasedCompiler(Protocol):
    @property
    def diagram_type(self) -> type[MermaidDiagram]: ...

    def compile(self, diagram: MermaidDiagram) -> str: ...


class CompilerRegistry:
    """Immutable exact-type compiler registry with explicit conflict semantics."""

    def __init__(self) -> None:
        self._compilers: Mapping[type[MermaidDiagram], _ErasedCompiler] = MappingProxyType({})

    @classmethod
    def _from_erased(cls, compilers: Mapping[type[MermaidDiagram], _ErasedCompiler]) -> CompilerRegistry:
        registry = cls()
        registry._compilers = MappingProxyType(dict(compilers))
        return registry

    @staticmethod
    def _validated_compiler(compiler: object) -> _ErasedCompiler:
        diagram_type = getattr(compiler, "diagram_type", None)
        compile_method = getattr(compiler, "compile", None)
        if not isinstance(diagram_type, type):
            raise CompilerRegistrationError("Compiler diagram_type must be a diagram class")
        if not callable(compile_method):
            raise CompilerRegistrationError("Compiler compile must be callable")
        return cast(_ErasedCompiler, compiler)

    @classmethod
    def empty(cls) -> CompilerRegistry:
        return cls()

    @property
    def registered_types(self) -> tuple[type[MermaidDiagram], ...]:
        return tuple(self._compilers)

    def _compiler_for(self, diagram: MermaidDiagram) -> _ErasedCompiler:
        try:
            return self._compilers[type(diagram)]
        except KeyError as error:
            raise UnsupportedDiagramError(f"No compiler registered for exact type {type(diagram).__name__}") from error

    def with_compiler[DiagramT: MermaidDiagram](self, compiler: DiagramCompiler[DiagramT]) -> CompilerRegistry:
        erased = self._validated_compiler(compiler)
        if erased.diagram_type in self._compilers:
            raise DuplicateCompilerError(f"Compiler already registered for {erased.diagram_type.__name__}")
        return self._from_erased({**self._compilers, erased.diagram_type: erased})

    def without(self, diagram_type: type[MermaidDiagram]) -> CompilerRegistry:
        if diagram_type not in self._compilers:
            raise CompilerRegistrationError(f"No compiler registered for {diagram_type.__name__}")
        return self._from_erased(
            {registered: compiler for registered, compiler in self._compilers.items() if registered is not diagram_type}
        )

    def replace[DiagramT: MermaidDiagram](self, compiler: DiagramCompiler[DiagramT]) -> CompilerRegistry:
        erased = self._validated_compiler(compiler)
        if erased.diagram_type not in self._compilers:
            raise CompilerRegistrationError(f"No compiler registered for {erased.diagram_type.__name__}")
        return self._from_erased(
            {
                registered: erased if registered is erased.diagram_type else current
                for registered, current in self._compilers.items()
            }
        )

    def merge(self, other: CompilerRegistry) -> CompilerRegistry:
        duplicates = set(self._compilers) & set(other._compilers)
        if duplicates:
            names = sorted(value.__name__ for value in duplicates)
            raise DuplicateCompilerError(f"Compilers already registered for: {names}")
        return self._from_erased({**self._compilers, **other._compilers})

    def compile(self, diagram: MermaidDiagram) -> str:
        compiler = self._compiler_for(diagram)
        try:
            return compiler.compile(diagram)
        except Exception as error:
            raise DiagramCompilationError(diagram.kind, type(compiler)) from error
