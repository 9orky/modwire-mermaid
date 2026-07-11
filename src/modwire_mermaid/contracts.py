from collections.abc import Collection, Hashable, Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, StringConstraints

ModwireDiagramIdentifier = Annotated[str, StringConstraints(pattern=r"^[\w-]+$")]


@dataclass(frozen=True)
class ModwireSyntaxFeature:
    docs_slug: str
    evidence_test: str


class ModwireDiagramDirection(StrEnum):
    TOP_BOTTOM = "TB"
    BOTTOM_TOP = "BT"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"


class ModwireDiagramError(ValueError):
    """Report an invalid diagram contract or unsupported diagram operation."""

    pass


class ModwireDiagramContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class ModwireBaseDiagram(ModwireDiagramContract):
    docs_url: ClassVar[str] = ""
    syntax_features: ClassVar[tuple[ModwireSyntaxFeature, ...]] = ()

    def _require_children(self, children: Collection[object], label: str) -> None:
        if not children:
            raise ModwireDiagramError(f"{label} must contain at least one child")

    def _validate_unique_children(self, identifiers: Iterable[Hashable], label: str) -> None:
        values = tuple(identifiers)
        if len(values) != len(set(values)):
            raise ModwireDiagramError(f"{label} children must be unique")

    def _validate_child_references(
        self,
        identifiers: Iterable[Hashable],
        references: Iterable[Hashable],
        label: str,
    ) -> None:
        unresolved = set(references) - set(identifiers)
        if unresolved:
            raise ModwireDiagramError(f"{label} reference unknown children: {sorted(unresolved)}")
