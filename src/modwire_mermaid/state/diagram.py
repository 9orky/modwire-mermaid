from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import model_validator

from ..contracts import (
    ModwireBaseDiagram,
    ModwireDiagramContract,
    ModwireDiagramDirection,
    ModwireDiagramIdentifier,
    ModwireMultilineText,
    ModwireOptionalText,
    ModwireStateReference,
    ModwireStyleName,
    ModwireStyleValue,
    ModwireSyntaxFeature,
    ModwireText,
)


class ModwireStateKind(StrEnum):
    SIMPLE = "state"
    CHOICE = "choice"
    FORK = "fork"
    JOIN = "join"


class ModwireState(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    label: ModwireMultilineText
    kind: ModwireStateKind = ModwireStateKind.SIMPLE
    children: tuple[ModwireState, ...] = ()
    transitions: tuple[ModwireStateTransition, ...] = ()
    concurrent_regions: tuple[tuple[ModwireDiagramIdentifier, ...], ...] = ()
    direction: ModwireDiagramDirection | Literal[""] = ""


class ModwireStateTransition(ModwireDiagramContract):
    source: ModwireStateReference
    target: ModwireStateReference
    label: ModwireOptionalText = ""


class ModwireStateNotePosition(StrEnum):
    LEFT = "left"
    RIGHT = "right"


class ModwireStateNote(ModwireDiagramContract):
    state_id: ModwireDiagramIdentifier
    position: ModwireStateNotePosition
    text: ModwireText


class ModwireStateStyleProperty(ModwireDiagramContract):
    name: ModwireStyleName
    value: ModwireStyleValue


class ModwireStateStyleDefinition(ModwireDiagramContract):
    name: ModwireDiagramIdentifier
    properties: tuple[ModwireStateStyleProperty, ...] = ()


class ModwireStateStyleAssignment(ModwireDiagramContract):
    state_ids: tuple[ModwireDiagramIdentifier, ...]
    style_names: tuple[ModwireDiagramIdentifier, ...]


class ModwireStateDiagram(ModwireBaseDiagram):
    kind: Literal["state"] = "state"
    docs_url = "https://mermaid.js.org/syntax/stateDiagram.html"
    syntax_features = (
        ModwireSyntaxFeature("choice", "test_state_supports_composites_notes_accessibility_and_styles"),
        ModwireSyntaxFeature("comments", "test_state_supports_composites_notes_accessibility_and_styles"),
        ModwireSyntaxFeature("composite-states", "test_state_supports_composites_notes_accessibility_and_styles"),
        ModwireSyntaxFeature("concurrency", "test_state_supports_composites_notes_accessibility_and_styles"),
        ModwireSyntaxFeature("forks", "test_state_supports_composites_notes_accessibility_and_styles"),
        ModwireSyntaxFeature("notes", "test_state_supports_composites_notes_accessibility_and_styles"),
        ModwireSyntaxFeature(
            "setting-the-direction-of-the-diagram", "test_state_supports_composites_notes_accessibility_and_styles"
        ),
        ModwireSyntaxFeature("start-and-end", "test_state_supports_composites_notes_accessibility_and_styles"),
        ModwireSyntaxFeature("states", "test_state_supports_composites_notes_accessibility_and_styles"),
        ModwireSyntaxFeature("styling-with-classdefs", "test_state_supports_composites_notes_accessibility_and_styles"),
        ModwireSyntaxFeature("transitions", "test_state_supports_composites_notes_accessibility_and_styles"),
    )

    states: tuple[ModwireState, ...]
    transitions: tuple[ModwireStateTransition, ...] = ()
    direction: ModwireDiagramDirection = ModwireDiagramDirection.TOP_BOTTOM
    comments: tuple[ModwireText, ...] = ()
    notes: tuple[ModwireStateNote, ...] = ()
    style_definitions: tuple[ModwireStateStyleDefinition, ...] = ()
    style_assignments: tuple[ModwireStateStyleAssignment, ...] = ()
    accessibility_title: ModwireOptionalText = ""
    accessibility_description: ModwireOptionalText = ""

    @model_validator(mode="after")
    def validate_states(self):
        self._require_children(self.states, "State diagram")
        located_states = self._located_states(self.states, ("states",))
        ids = tuple(state.id for _, state in located_states)
        self._validate_unique_children(ids, "State diagram")
        self._validate_located_references(
            ids,
            (
                (("transitions", index, field), value)
                for index, item in enumerate(self.transitions)
                for field, value in (("source", item.source), ("target", item.target))
                if value != "[*]"
            ),
            "State",
        )
        self._validate_located_references(
            ids,
            (
                ((*path, "transitions", transition_index, field), value)
                for path, state in located_states
                for transition_index, transition in enumerate(state.transitions)
                for field, value in (("source", transition.source), ("target", transition.target))
                if value != "[*]"
            ),
            "Nested state transition",
        )
        self._validate_located_references(
            ids,
            (
                ((*path, "concurrent_regions", region_index, state_index), state_id)
                for path, state in located_states
                for region_index, region in enumerate(state.concurrent_regions)
                for state_index, state_id in enumerate(region)
            ),
            "Concurrent state region",
        )
        self._validate_located_references(
            ids,
            ((("notes", index, "state_id"), note.state_id) for index, note in enumerate(self.notes)),
            "State note",
        )
        self._validate_located_references(
            ids,
            (
                (("style_assignments", assignment_index, "state_ids", state_index), state_id)
                for assignment_index, assignment in enumerate(self.style_assignments)
                for state_index, state_id in enumerate(assignment.state_ids)
            ),
            "State style",
        )
        style_names = tuple(style.name for style in self.style_definitions)
        self._validate_unique_children(style_names, "State style definition")
        self._validate_located_references(
            style_names,
            (
                (("style_assignments", assignment_index, "style_names", name_index), name)
                for assignment_index, assignment in enumerate(self.style_assignments)
                for name_index, name in enumerate(assignment.style_names)
            ),
            "State style definition",
        )
        return self

    def _located_states(
        self, states: tuple[ModwireState, ...], prefix: tuple[str | int, ...]
    ) -> tuple[tuple[tuple[str | int, ...], ModwireState], ...]:
        result: list[tuple[tuple[str | int, ...], ModwireState]] = []
        for index, state in enumerate(states):
            path = (*prefix, index)
            result.append((path, state))
            result.extend(self._located_states(state.children, (*path, "children")))
        return tuple(result)
