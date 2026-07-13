from collections.abc import Collection, Hashable, Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated, ClassVar, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel, ConfigDict, StringConstraints

ModwireDiagramIdentifier = Annotated[str, StringConstraints(pattern=r"^[\w-]+$")]
NonBlankSingleLine = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\r\n]+$")]


@dataclass(frozen=True)
class ModwireSyntaxFeature:
    docs_slug: str
    evidence_test: str


class ModwireDiagramDirection(StrEnum):
    TOP_DOWN = "TD"
    TOP_BOTTOM = "TB"
    BOTTOM_TOP = "BT"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"


class ModwireMermaidError(Exception):
    """Base class for operational modwire-mermaid failures."""


class DiagramBuildError(ModwireMermaidError):
    """Report invalid ordering or missing context in a diagram builder."""


class CompilerRegistrationError(ModwireMermaidError):
    """Report an invalid compiler registry operation."""


class DuplicateCompilerError(CompilerRegistrationError):
    """Report an attempt to register the same exact diagram type twice."""


class UnsupportedDiagramError(ModwireMermaidError):
    """Report a diagram whose exact type has no registered compiler."""


class DiagramCompilationError(ModwireMermaidError):
    """Wrap a selected compiler failure with stable diagram context."""

    def __init__(self, diagram_kind: str, compiler_type: type[object]):
        self.diagram_kind = diagram_kind
        self.compiler_type = compiler_type
        super().__init__(f"{compiler_type.__name__} failed to compile {diagram_kind!r}")


@runtime_checkable
class MermaidDiagram(Protocol):
    """Structural contract accepted by compiler registries and the façade."""

    @property
    def kind(self) -> str: ...


BuiltDiagramT = TypeVar("BuiltDiagramT", bound=MermaidDiagram, covariant=True)


class DiagramBuilder(Protocol[BuiltDiagramT]):
    """Build one validated diagram without exposing mutable intermediate state."""

    def build(self) -> BuiltDiagramT: ...


class ModwireDiagramContract(BaseModel):
    """Strict frozen Pydantic base for all bundled semantic contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class ModwireBaseDiagram(ModwireDiagramContract):
    """Recommended Pydantic base for built-in and external diagrams."""

    docs_url: ClassVar[str] = ""
    syntax_features: ClassVar[tuple[ModwireSyntaxFeature, ...]] = ()

    def _require_children(self, children: Collection[object], label: str) -> None:
        if not children:
            raise ValueError(f"{label} must contain at least one child")

    def _validate_unique_children(self, identifiers: Iterable[Hashable], label: str) -> None:
        values = tuple(identifiers)
        if len(values) != len(set(values)):
            raise ValueError(f"{label} children must be unique")

    def _validate_child_references(
        self,
        identifiers: Iterable[Hashable],
        references: Iterable[Hashable],
        label: str,
    ) -> None:
        unresolved = set(references) - set(identifiers)
        if unresolved:
            raise ValueError(f"{label} reference unknown children: {sorted(map(str, unresolved))}")
