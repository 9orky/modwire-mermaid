from enum import StrEnum

from pydantic import model_validator

from ..contracts import (
    ModwireBaseDiagram,
    ModwireDiagramContract,
    ModwireDiagramError,
    ModwireDiagramIdentifier,
    ModwireSyntaxFeature,
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
    data_type: ModwireEventDataType
    data: str


class ModwireEventTimeframe(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    entity_type: ModwireEventEntityType
    entity: str
    is_reset: bool
    data_type: ModwireEventDataType
    data: str
    data_block_id: str
    relations: tuple[ModwireDiagramIdentifier, ...]


class ModwireEventModel(ModwireBaseDiagram):
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
    data_blocks: tuple[ModwireEventDataBlock, ...]

    @model_validator(mode="after")
    def validate_model(self):
        self._require_children(self.timeframes, "Event model")
        ids = tuple(item.id for item in self.timeframes)
        self._validate_unique_children(ids, "Event model")
        self._validate_child_references(
            ids, (value for item in self.timeframes for value in item.relations), "Event-model relation"
        )
        block_ids = tuple(item.id for item in self.data_blocks)
        self._validate_unique_children(block_ids, "Event-model data blocks")
        self._validate_child_references(
            block_ids,
            (item.data_block_id for item in self.timeframes if item.data_block_id),
            "Event-model data block",
        )
        if any(item.data and item.data_block_id for item in self.timeframes):
            raise ModwireDiagramError("Event-model timeframes cannot use inline data and a data block together")
        return self
