from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import model_validator

from ..contracts import DiagramBuildError, ModwireBaseDiagram, ModwireDiagramContract, ModwireSyntaxFeature


class ModwireTimelinePeriod(ModwireDiagramContract):
    name: str
    events: tuple[str, ...]


class ModwireTimelineSection(ModwireDiagramContract):
    name: str
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
    title: str = ""
    direction: ModwireTimelineDirection = ModwireTimelineDirection.LEFT_RIGHT
    disable_multicolor: bool = False

    @model_validator(mode="after")
    def validate_timeline(self):
        self._require_children(self.sections, "Timeline")
        if any(not section.periods for section in self.sections):
            raise ValueError("Every timeline section must contain a period")
        if any(not period.events for section in self.sections for period in section.periods):
            raise ValueError("Every timeline period must contain an event")
        return self


class ModwireTimelineBuilder:
    def __init__(
        self,
        title: str,
        sections: tuple[ModwireTimelineSection, ...],
        direction: ModwireTimelineDirection,
        disable_multicolor: bool,
    ):
        self._title = title
        self._sections = sections
        self._direction = direction
        self._disable_multicolor = disable_multicolor

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
