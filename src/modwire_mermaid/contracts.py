from collections.abc import Collection, Hashable, Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated, ClassVar, LiteralString, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError

ModwireDiagramIdentifier = Annotated[str, StringConstraints(pattern=r"^[\w-]+$")]
ModwireDiagramReference = Annotated[str, StringConstraints(pattern=r"^$|^[\w-]+$")]
ModwireNamespaceIdentifier = Annotated[str, StringConstraints(pattern=r"^[\w-]+(?:\.[\w-]+)*$")]
ModwireNamespaceReference = Annotated[str, StringConstraints(pattern=r"^$|^[\w-]+(?:\.[\w-]+)*$")]
ModwireStateReference = Annotated[str, StringConstraints(pattern=r"^(?:\[\*\]|[\w-]+)$")]
ModwireSingleLine = Annotated[str, StringConstraints(pattern=r"^[^\r\n]*$")]
ModwireText = Annotated[str, StringConstraints(pattern=r"^[^\r\n]*\S[^\r\n]*$")]
ModwireOptionalText = Annotated[str, StringConstraints(pattern=r"^(?:|[^\r\n]*\S[^\r\n]*)$")]
ModwireSyntaxToken = Annotated[str, StringConstraints(pattern=r"^[^\r\n{};]*\S[^\r\n{};]*$")]
ModwireOptionalSyntaxToken = Annotated[str, StringConstraints(pattern=r"^(?:|[^\r\n{};]*\S[^\r\n{};]*)$")]
ModwireMultilineText = Annotated[str, StringConstraints(min_length=1)]
ModwireCssName = Annotated[str, StringConstraints(pattern=r"^[A-Za-z_][A-Za-z0-9_-]*$")]
ModwireIconName = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9_:-]+$")]
ModwireOptionalIconName = Annotated[str, StringConstraints(pattern=r"^$|^[A-Za-z0-9_:-]+$")]
ModwireStyleName = Annotated[str, StringConstraints(pattern=r"^[A-Za-z-][A-Za-z0-9_-]*$")]
ModwireStyleValue = Annotated[str, StringConstraints(pattern=r"^[^\r\n;]+$")]
ModwireConfigValue = Annotated[str, StringConstraints(pattern=r"^(?:|[^\r\n;]*\S[^\r\n;]*)$")]
ModwireColor = ModwireConfigValue
MODWIRE_URL_PATTERN = r"^[^\s\r\n]+$"
MODWIRE_CALLBACK_PATTERN = r"^[A-Za-z_][A-Za-z0-9_.]*$"
ModwireUrl = Annotated[str, StringConstraints(pattern=MODWIRE_URL_PATTERN)]
ModwireCallbackName = Annotated[str, StringConstraints(pattern=MODWIRE_CALLBACK_PATTERN)]
ModwirePositiveInt = Annotated[int, Field(gt=0)]
ModwireNonNegativeInt = Annotated[int, Field(ge=0)]
NonBlankSingleLine = ModwireText


@dataclass(frozen=True)
class ModwireSyntaxFeature:
    docs_slug: str
    evidence_test: str


@dataclass(frozen=True)
class ModwireContractViolation:
    location: tuple[str | int, ...]
    code: LiteralString
    message: LiteralString
    input: object
    context: dict[str, object] | None = None


def contract_validation_error(model_name: str, violations: Iterable[ModwireContractViolation]) -> ValidationError:
    errors: list[InitErrorDetails] = []
    for violation in violations:
        errors.append(
            InitErrorDetails(
                type=PydanticCustomError(violation.code, violation.message, violation.context),
                loc=violation.location,
                input=violation.input,
            )
        )
    return ValidationError.from_exception_data(model_name, errors)


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

    def _validate_located_references(
        self,
        identifiers: Iterable[Hashable],
        references: Iterable[tuple[tuple[str | int, ...], Hashable]],
        label: str,
    ) -> None:
        allowed = set(identifiers)
        violations = tuple(
            ModwireContractViolation(
                location=location,
                code="unknown_reference",
                message="{label} reference {reference} does not exist",
                input=reference,
                context={"label": label, "reference": reference},
            )
            for location, reference in references
            if reference not in allowed
        )
        if violations:
            raise contract_validation_error(type(self).__name__, violations)
