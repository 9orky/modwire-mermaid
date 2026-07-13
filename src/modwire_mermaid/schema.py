from typing import Any

from .diagrams import DiagramAdapter

DIAGRAM_SCHEMA_VERSION = "2"
DIAGRAM_SCHEMA_ID = "https://modwire.dev/schemas/modwire-mermaid/v2/diagram.schema.json"


def diagram_json_schema() -> dict[str, Any]:
    """Return the canonical versioned schema for every bundled diagram."""
    generated = DiagramAdapter.json_schema()
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": DIAGRAM_SCHEMA_ID,
        **generated,
    }
