from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from ..contracts import (
    ModwireBaseDiagram,
    ModwireDiagramContract,
    ModwireDiagramDirection,
    ModwireDiagramIdentifier,
    ModwireSyntaxFeature,
)


class ModwireStateKind(StrEnum):
    SIMPLE = "state"
    CHOICE = "choice"
    FORK = "fork"
    JOIN = "join"


class ModwireState(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    label: str
    kind: ModwireStateKind
    children: tuple[ModwireState, ...]
    transitions: tuple[ModwireStateTransition, ...]
    concurrent_regions: tuple[tuple[ModwireDiagramIdentifier, ...], ...]
    direction: str


class ModwireStateTransition(ModwireDiagramContract):
    source: str
    target: str
    label: str


class ModwireStateNotePosition(StrEnum):
    LEFT = "left"
    RIGHT = "right"


class ModwireStateNote(ModwireDiagramContract):
    state_id: ModwireDiagramIdentifier
    position: ModwireStateNotePosition
    text: str


class ModwireStateStyleProperty(ModwireDiagramContract):
    name: str
    value: str

    def mermaid(self) -> str:
        return f"{self.name}:{self.value}"


class ModwireStateStyleDefinition(ModwireDiagramContract):
    name: ModwireDiagramIdentifier
    properties: tuple[ModwireStateStyleProperty, ...]


class ModwireStateStyleAssignment(ModwireDiagramContract):
    state_ids: tuple[ModwireDiagramIdentifier, ...]
    style_names: tuple[ModwireDiagramIdentifier, ...]


class ModwireStateDiagram(ModwireBaseDiagram):
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
    transitions: tuple[ModwireStateTransition, ...]
    direction: ModwireDiagramDirection
    comments: tuple[str, ...]
    notes: tuple[ModwireStateNote, ...]
    style_definitions: tuple[ModwireStateStyleDefinition, ...]
    style_assignments: tuple[ModwireStateStyleAssignment, ...]
    accessibility_title: str
    accessibility_description: str

    @model_validator(mode="after")
    def validate_states(self):
        self._require_children(self.states, "State diagram")
        ids = self._state_ids(self.states)
        self._validate_unique_children(ids, "State diagram")
        references = tuple(value for item in self.transitions for value in (item.source, item.target) if value != "[*]")
        self._validate_child_references(ids, references, "State")
        self._validate_child_references(ids, (note.state_id for note in self.notes), "State note")
        self._validate_child_references(
            ids,
            (state_id for assignment in self.style_assignments for state_id in assignment.state_ids),
            "State style",
        )
        return self

    def _state_ids(self, states: tuple[ModwireState, ...]) -> tuple[str, ...]:
        return tuple(state.id for state in states) + tuple(
            child_id for state in states for child_id in self._state_ids(state.children)
        )
