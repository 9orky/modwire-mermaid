from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from pydantic import model_validator

from ..contracts import (
    DiagramBuildError,
    ModwireBaseDiagram,
    ModwireContractViolation,
    ModwireDiagramContract,
    ModwireOptionalText,
    ModwireSyntaxFeature,
    ModwireText,
    contract_validation_error,
)


class ModwireTimelinePeriod(ModwireDiagramContract):
    name: ModwireText
    events: tuple[ModwireText, ...]


class ModwireTimelineSection(ModwireDiagramContract):
    name: ModwireText
    periods: tuple[ModwireTimelinePeriod, ...]


class ModwireTimelineDirection(StrEnum):
    LEFT_RIGHT = "LR"
    TOP_DOWN = "TD"


class ModwireTimeline(ModwireBaseDiagram):
    kind: Literal["timeline"] = "timeline"
    docs_url = "https://mermaid.js.org/syntax/timeline.html"
    syntax_features = (
        ModwireSyntaxFeature("direction-v11140", "test_timeline_compiles_sections_direction_and_configuration"),
        ModwireSyntaxFeature(
            "grouping-of-time-periods-in-sectionsages", "test_timeline_compiles_sections_direction_and_configuration"
        ),
        ModwireSyntaxFeature(
            "styling-of-time-periods-and-events", "test_timeline_compiles_sections_direction_and_configuration"
        ),
        ModwireSyntaxFeature("syntax", "test_timeline_compiles_sections_direction_and_configuration"),
    )

    sections: tuple[ModwireTimelineSection, ...]
    title: ModwireOptionalText = ""
    direction: ModwireTimelineDirection = ModwireTimelineDirection.LEFT_RIGHT
    disable_multicolor: bool = False

    @model_validator(mode="after")
    def validate_timeline(self):
        self._require_children(self.sections, "Timeline")
        violations = tuple(
            ModwireContractViolation(
                ("sections", index, "periods"),
                "missing_child",
                "Every timeline section must contain a period",
                section.periods,
            )
            for index, section in enumerate(self.sections)
            if not section.periods
        ) + tuple(
            ModwireContractViolation(
                ("sections", section_index, "periods", period_index, "events"),
                "missing_child",
                "Every timeline period must contain an event",
                period.events,
            )
            for section_index, section in enumerate(self.sections)
            for period_index, period in enumerate(section.periods)
            if not period.events
        )
        if violations:
            raise contract_validation_error(type(self).__name__, violations)
        return self


@dataclass(frozen=True, slots=True)
class ModwireTimelineBuilder:
    _title: str
    _sections: tuple[ModwireTimelineSection, ...]
    _direction: ModwireTimelineDirection
    _disable_multicolor: bool

    @classmethod
    def create(
        cls,
        title: str,
        direction: ModwireTimelineDirection = ModwireTimelineDirection.LEFT_RIGHT,
        disable_multicolor: bool = False,
    ) -> ModwireTimelineBuilder:
        return cls(title, (), direction, disable_multicolor)

    def section(self, name: str) -> ModwireTimelineBuilder:
        section = ModwireTimelineSection(name=name, periods=())
        return ModwireTimelineBuilder(
            self._title,
            (*self._sections, section),
            self._direction,
            self._disable_multicolor,
        )

    def period(self, name: str, *events: str) -> ModwireTimelineBuilder:
        if not self._sections:
            raise DiagramBuildError("Add a timeline section before adding a period")
        current = self._sections[-1]
        updated = ModwireTimelineSection(
            name=current.name,
            periods=(*current.periods, ModwireTimelinePeriod(name=name, events=events)),
        )
        return ModwireTimelineBuilder(
            self._title,
            (*self._sections[:-1], updated),
            self._direction,
            self._disable_multicolor,
        )

    def build(self) -> ModwireTimeline:
        return ModwireTimeline(
            title=self._title,
            sections=self._sections,
            direction=self._direction,
            disable_multicolor=self._disable_multicolor,
        )
