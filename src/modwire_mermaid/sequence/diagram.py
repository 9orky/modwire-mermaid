from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from ..contracts import (
    ModwireBaseDiagram,
    ModwireDiagramContract,
    ModwireDiagramError,
    ModwireDiagramIdentifier,
    ModwireSyntaxFeature,
)


class ModwireSequenceParticipantKind(StrEnum):
    PARTICIPANT = "participant"
    ACTOR = "actor"
    BOUNDARY = "boundary"
    CONTROL = "control"
    ENTITY = "entity"
    DATABASE = "database"
    COLLECTIONS = "collections"
    QUEUE = "queue"


class ModwireSequenceLink(ModwireDiagramContract):
    label: str
    url: str


class ModwireSequenceParticipant(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    label: str
    kind: ModwireSequenceParticipantKind
    links: tuple[ModwireSequenceLink, ...]
    box: str
    box_color: str


class ModwireSequenceArrow(StrEnum):
    SOLID = "->>"
    DOTTED = "-->>"
    SOLID_OPEN = "->"
    DOTTED_OPEN = "-->"
    SOLID_CROSS = "-x"
    DOTTED_CROSS = "--x"
    SOLID_ASYNC = "-)"
    DOTTED_ASYNC = "--)"


class ModwireSequenceMessage(ModwireDiagramContract):
    source: ModwireDiagramIdentifier
    target: ModwireDiagramIdentifier
    text: str
    arrow: ModwireSequenceArrow
    activate_target: bool
    deactivate_target: bool
    central_source: bool
    central_target: bool


class ModwireSequenceLifecycleKind(StrEnum):
    CREATE = "create"
    DESTROY = "destroy"


class ModwireSequenceLifecycle(ModwireDiagramContract):
    participant_id: ModwireDiagramIdentifier
    kind: ModwireSequenceLifecycleKind


class ModwireSequenceActivationKind(StrEnum):
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"


class ModwireSequenceActivation(ModwireDiagramContract):
    participant_id: ModwireDiagramIdentifier
    kind: ModwireSequenceActivationKind


class ModwireSequenceNotePosition(StrEnum):
    LEFT = "left of"
    RIGHT = "right of"
    OVER = "over"


class ModwireSequenceNote(ModwireDiagramContract):
    participant_ids: tuple[ModwireDiagramIdentifier, ...]
    position: ModwireSequenceNotePosition
    text: str


class ModwireSequenceBlockKind(StrEnum):
    LOOP = "loop"
    OPTIONAL = "opt"
    ALTERNATIVE = "alt"
    PARALLEL = "par"
    CRITICAL = "critical"
    BREAK = "break"


class ModwireSequenceBranch(ModwireDiagramContract):
    label: str
    statements: tuple[ModwireSequenceStatement, ...]


class ModwireSequenceBlock(ModwireDiagramContract):
    kind: ModwireSequenceBlockKind
    label: str
    statements: tuple[ModwireSequenceStatement, ...]
    branches: tuple[ModwireSequenceBranch, ...]


class ModwireSequenceRect(ModwireDiagramContract):
    color: str
    statements: tuple[ModwireSequenceStatement, ...]


ModwireSequenceStatement = (
    ModwireSequenceMessage
    | ModwireSequenceLifecycle
    | ModwireSequenceActivation
    | ModwireSequenceNote
    | ModwireSequenceBlock
    | ModwireSequenceRect
)


class ModwireSequenceDiagram(ModwireBaseDiagram):
    docs_url = "https://mermaid.js.org/syntax/sequenceDiagram.html"
    syntax_features = (
        ModwireSyntaxFeature("activations", "test_sequence_supports_links_notes_and_control_blocks"),
        ModwireSyntaxFeature("actors", "test_sequence_supports_links_notes_and_control_blocks"),
        ModwireSyntaxFeature("alt", "test_sequence_supports_links_notes_and_control_blocks"),
        ModwireSyntaxFeature("background-highlighting", "test_sequence_supports_links_notes_and_control_blocks"),
        ModwireSyntaxFeature("break", "test_sequence_supports_links_notes_and_control_blocks"),
        ModwireSyntaxFeature("comments", "test_sequence_supports_links_notes_and_control_blocks"),
        ModwireSyntaxFeature("critical-region", "test_sequence_supports_links_notes_and_control_blocks"),
        ModwireSyntaxFeature(
            "entity-codes-to-escape-characters", "test_sequence_supports_links_notes_and_control_blocks"
        ),
        ModwireSyntaxFeature("grouping--box", "test_sequence_supports_links_notes_and_control_blocks"),
        ModwireSyntaxFeature("loops", "test_sequence_supports_links_notes_and_control_blocks"),
        ModwireSyntaxFeature("messages", "test_sequence_supports_links_notes_and_control_blocks"),
        ModwireSyntaxFeature("notes", "test_sequence_supports_links_notes_and_control_blocks"),
        ModwireSyntaxFeature("parallel", "test_sequence_supports_links_notes_and_control_blocks"),
        ModwireSyntaxFeature("participants", "test_sequence_supports_links_notes_and_control_blocks"),
    )

    participants: tuple[ModwireSequenceParticipant, ...]
    statements: tuple[ModwireSequenceStatement, ...]
    autonumber: bool
    title: str
    comments: tuple[str, ...]

    @model_validator(mode="after")
    def validate_sequence(self):
        self._require_children(self.participants, "Sequence diagram")
        identifiers = tuple(item.id for item in self.participants)
        self._validate_unique_children(identifiers, "Sequence diagram")
        statements = self._flatten(self.statements)
        messages = tuple(item for item in statements if isinstance(item, ModwireSequenceMessage))
        self._validate_child_references(
            identifiers,
            (value for message in messages for value in (message.source, message.target)),
            "Sequence message",
        )
        self._validate_child_references(
            identifiers,
            (item.participant_id for item in statements if isinstance(item, ModwireSequenceActivation)),
            "Sequence activation",
        )
        self._validate_child_references(
            identifiers,
            (item.participant_id for item in statements if isinstance(item, ModwireSequenceLifecycle)),
            "Sequence lifecycle",
        )
        self._validate_child_references(
            identifiers,
            (value for item in statements if isinstance(item, ModwireSequenceNote) for value in item.participant_ids),
            "Sequence note",
        )
        if any(message.activate_target and message.deactivate_target for message in messages):
            raise ModwireDiagramError("A sequence message cannot activate and deactivate its target")
        if any(
            isinstance(item, ModwireSequenceNote) and (not item.participant_ids or len(item.participant_ids) > 2)
            for item in statements
        ):
            raise ModwireDiagramError("Sequence notes require one or two participants")
        return self

    def _flatten(self, values: tuple[ModwireSequenceStatement, ...]) -> tuple[ModwireSequenceStatement, ...]:
        result: list[ModwireSequenceStatement] = []
        for value in values:
            result.append(value)
            if isinstance(value, ModwireSequenceBlock):
                result.extend(self._flatten(value.statements))
                for branch in value.branches:
                    result.extend(self._flatten(branch.statements))
            elif isinstance(value, ModwireSequenceRect):
                result.extend(self._flatten(value.statements))
        return tuple(result)
