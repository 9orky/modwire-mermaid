from enum import StrEnum
from typing import Literal

from pydantic import model_validator

from ..contracts import (
    ModwireBaseDiagram,
    ModwireContractViolation,
    ModwireDiagramContract,
    ModwireDiagramIdentifier,
    ModwireDiagramReference,
    ModwireOptionalText,
    ModwireSyntaxFeature,
    contract_validation_error,
)


class ModwireEventEntityType(StrEnum):
    UI = "ui"
    PROCESSOR = "pcr"
    COMMAND = "cmd"
    READ_MODEL = "rmo"
    EVENT = "evt"


class ModwireEventDataType(StrEnum):
    NONE = ""
    JSON = "json"
    JAVASCRIPT_OBJECT = "jsobj"
    FIGMA = "figma"
    SALT = "salt"
    URI = "uri"
    MARKDOWN = "md"
    HTML = "html"
    TEXT = "text"


class ModwireEventDataBlock(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    data_type: ModwireEventDataType = ModwireEventDataType.NONE
    data: ModwireOptionalText = ""


class ModwireEventTimeframe(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    entity_type: ModwireEventEntityType
    entity: ModwireOptionalText = ""
    is_reset: bool = False
    data_type: ModwireEventDataType = ModwireEventDataType.NONE
    data: ModwireOptionalText = ""
    data_block_id: ModwireDiagramReference = ""
    relations: tuple[ModwireDiagramIdentifier, ...] = ()


class ModwireEventModel(ModwireBaseDiagram):
    kind: Literal["event-modeling"] = "event-modeling"
    docs_url = "https://mermaid.js.org/syntax/eventmodeling.html"
    syntax_features = (
        ModwireSyntaxFeature("data-block", "test_event_modeling_supports_reset_relations_and_typed_data_blocks"),
        ModwireSyntaxFeature(
            "data-block-data-types", "test_event_modeling_supports_reset_relations_and_typed_data_blocks"
        ),
        ModwireSyntaxFeature("entity-types", "test_event_modeling_supports_reset_relations_and_typed_data_blocks"),
        ModwireSyntaxFeature("inline-data", "test_event_modeling_supports_reset_relations_and_typed_data_blocks"),
        ModwireSyntaxFeature(
            "multiple-relations", "test_event_modeling_supports_reset_relations_and_typed_data_blocks"
        ),
        ModwireSyntaxFeature(
            "resetting-the-flow", "test_event_modeling_supports_reset_relations_and_typed_data_blocks"
        ),
        ModwireSyntaxFeature(
            "swimlanes-and-namespaces", "test_event_modeling_supports_reset_relations_and_typed_data_blocks"
        ),
        ModwireSyntaxFeature("timeline", "test_event_modeling_supports_reset_relations_and_typed_data_blocks"),
    )

    timeframes: tuple[ModwireEventTimeframe, ...]
    data_blocks: tuple[ModwireEventDataBlock, ...] = ()

    @model_validator(mode="after")
    def validate_model(self):
        self._require_children(self.timeframes, "Event model")
        ids = tuple(item.id for item in self.timeframes)
        self._validate_unique_children(ids, "Event model")
        self._validate_located_references(
            ids,
            (
                (("timeframes", timeframe_index, "relations", relation_index), relation)
                for timeframe_index, item in enumerate(self.timeframes)
                for relation_index, relation in enumerate(item.relations)
            ),
            "Event-model relation",
        )
        block_ids = tuple(item.id for item in self.data_blocks)
        self._validate_unique_children(block_ids, "Event-model data blocks")
        self._validate_located_references(
            block_ids,
            (
                (("timeframes", index, "data_block_id"), item.data_block_id)
                for index, item in enumerate(self.timeframes)
                if item.data_block_id
            ),
            "Event-model data block",
        )
        violations = tuple(
            ModwireContractViolation(
                ("timeframes", index, "data_block_id"),
                "invalid_configuration",
                "A timeframe cannot use inline data and a data block together",
                item.data_block_id,
            )
            for index, item in enumerate(self.timeframes)
            if item.data and item.data_block_id
        )
        if violations:
            raise contract_validation_error(type(self).__name__, violations)
        return self
