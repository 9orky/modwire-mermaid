from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, model_validator

from ..contracts import (
    ModwireBaseDiagram,
    ModwireColor,
    ModwireContractViolation,
    ModwireDiagramContract,
    ModwireDiagramIdentifier,
    ModwireOptionalText,
    ModwireSyntaxFeature,
    ModwireText,
    ModwireUrl,
    contract_validation_error,
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
    label: ModwireText
    url: ModwireUrl


class ModwireSequenceParticipant(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    label: ModwireText
    kind: ModwireSequenceParticipantKind = ModwireSequenceParticipantKind.PARTICIPANT
    links: tuple[ModwireSequenceLink, ...] = ()
    box: ModwireOptionalText = ""
    box_color: ModwireColor = ""


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
    statement_type: Literal["message"] = "message"
    source: ModwireDiagramIdentifier
    target: ModwireDiagramIdentifier
    text: ModwireText
    arrow: ModwireSequenceArrow = ModwireSequenceArrow.SOLID
    activate_target: bool = False
    deactivate_target: bool = False
    central_source: bool = False
    central_target: bool = False


class ModwireSequenceLifecycleKind(StrEnum):
    CREATE = "create"
    DESTROY = "destroy"


class ModwireSequenceLifecycle(ModwireDiagramContract):
    statement_type: Literal["lifecycle"] = "lifecycle"
    participant_id: ModwireDiagramIdentifier
    kind: ModwireSequenceLifecycleKind


class ModwireSequenceActivationKind(StrEnum):
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"


class ModwireSequenceActivation(ModwireDiagramContract):
    statement_type: Literal["activation"] = "activation"
    participant_id: ModwireDiagramIdentifier
    kind: ModwireSequenceActivationKind


class ModwireSequenceNotePosition(StrEnum):
    LEFT = "left of"
    RIGHT = "right of"
    OVER = "over"


class ModwireSequenceNote(ModwireDiagramContract):
    statement_type: Literal["note"] = "note"
    participant_ids: tuple[ModwireDiagramIdentifier, ...]
    position: ModwireSequenceNotePosition
    text: ModwireText


class ModwireSequenceBlockKind(StrEnum):
    LOOP = "loop"
    OPTIONAL = "opt"
    ALTERNATIVE = "alt"
    PARALLEL = "par"
    CRITICAL = "critical"
    BREAK = "break"


class ModwireSequenceBranch(ModwireDiagramContract):
    label: ModwireText
    statements: tuple[ModwireSequenceStatement, ...] = ()


class ModwireSequenceBlock(ModwireDiagramContract):
    statement_type: Literal["block"] = "block"
    kind: ModwireSequenceBlockKind
    label: ModwireText
    statements: tuple[ModwireSequenceStatement, ...] = ()
    branches: tuple[ModwireSequenceBranch, ...] = ()


class ModwireSequenceRect(ModwireDiagramContract):
    statement_type: Literal["rect"] = "rect"
    color: ModwireColor
    statements: tuple[ModwireSequenceStatement, ...] = ()


ModwireSequenceStatement = Annotated[
    ModwireSequenceMessage
    | ModwireSequenceLifecycle
    | ModwireSequenceActivation
    | ModwireSequenceNote
    | ModwireSequenceBlock
    | ModwireSequenceRect,
    Field(discriminator="statement_type"),
]


class ModwireSequenceDiagram(ModwireBaseDiagram):
    kind: Literal["sequence"] = "sequence"
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
    statements: tuple[ModwireSequenceStatement, ...] = ()
    autonumber: bool = False
    title: ModwireOptionalText = ""
    comments: tuple[ModwireText, ...] = ()

    @model_validator(mode="after")
    def validate_sequence(self):
        self._require_children(self.participants, "Sequence diagram")
        identifiers = tuple(item.id for item in self.participants)
        self._validate_unique_children(identifiers, "Sequence diagram")
        statements = self._located_statements(self.statements, ("statements",))
        messages = tuple((path, item) for path, item in statements if isinstance(item, ModwireSequenceMessage))
        self._validate_located_references(
            identifiers,
            (
                ((*path, field), value)
                for path, message in messages
                for field, value in (("source", message.source), ("target", message.target))
            ),
            "Sequence message",
        )
        self._validate_located_references(
            identifiers,
            (
                ((*path, "participant_id"), item.participant_id)
                for path, item in statements
                if isinstance(item, ModwireSequenceActivation)
            ),
            "Sequence activation",
        )
        self._validate_located_references(
            identifiers,
            (
                ((*path, "participant_id"), item.participant_id)
                for path, item in statements
                if isinstance(item, ModwireSequenceLifecycle)
            ),
            "Sequence lifecycle",
        )
        self._validate_located_references(
            identifiers,
            (
                ((*path, "participant_ids", index), value)
                for path, item in statements
                if isinstance(item, ModwireSequenceNote)
                for index, value in enumerate(item.participant_ids)
            ),
            "Sequence note",
        )
        invalid_messages = tuple(
            ModwireContractViolation(
                (*path, "deactivate_target"),
                "invalid_configuration",
                "A sequence message cannot activate and deactivate its target",
                message.deactivate_target,
            )
            for path, message in messages
            if message.activate_target and message.deactivate_target
        )
        invalid_notes = tuple(
            ModwireContractViolation(
                (*path, "participant_ids"),
                "invalid_configuration",
                "Sequence notes require one or two participants",
                item.participant_ids,
            )
            for path, item in statements
            if isinstance(item, ModwireSequenceNote) and (not item.participant_ids or len(item.participant_ids) > 2)
        )
        if invalid_messages or invalid_notes:
            raise contract_validation_error(type(self).__name__, (*invalid_messages, *invalid_notes))
        blocks = tuple((path, item) for path, item in statements if isinstance(item, ModwireSequenceBlock))
        for path, block in blocks:
            if block.branches and block.kind not in {
                ModwireSequenceBlockKind.ALTERNATIVE,
                ModwireSequenceBlockKind.PARALLEL,
                ModwireSequenceBlockKind.CRITICAL,
            }:
                raise contract_validation_error(
                    type(self).__name__,
                    (
                        ModwireContractViolation(
                            (*path, "branches"),
                            "invalid_configuration",
                            "This sequence block kind cannot contain branches",
                            block.branches,
                        ),
                    ),
                )
        return self

    def _located_statements(
        self, values: tuple[ModwireSequenceStatement, ...], prefix: tuple[str | int, ...]
    ) -> tuple[tuple[tuple[str | int, ...], ModwireSequenceStatement], ...]:
        result: list[tuple[tuple[str | int, ...], ModwireSequenceStatement]] = []
        for index, value in enumerate(values):
            path = (*prefix, index)
            result.append((path, value))
            if isinstance(value, ModwireSequenceBlock):
                result.extend(self._located_statements(value.statements, (*path, "statements")))
                for branch_index, branch in enumerate(value.branches):
                    result.extend(
                        self._located_statements(branch.statements, (*path, "branches", branch_index, "statements"))
                    )
            elif isinstance(value, ModwireSequenceRect):
                result.extend(self._located_statements(value.statements, (*path, "statements")))
        return tuple(result)
