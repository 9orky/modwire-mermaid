import argparse
import json
from pathlib import Path

from modwire_mermaid.schema import DIAGRAM_SCHEMA_VERSION, diagram_json_schema

ROOT = Path(__file__).parents[1]
TARGET = ROOT / "src" / "modwire_mermaid" / "schemas" / f"v{DIAGRAM_SCHEMA_VERSION}" / "diagram.schema.json"


def render_schema() -> str:
    return json.dumps(diagram_json_schema(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    rendered = render_schema()
    if arguments.check:
        if not TARGET.exists() or TARGET.read_text() != rendered:
            raise SystemExit(f"Schema artifact is stale: {TARGET}")
        return
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(rendered)


if __name__ == "__main__":
    main()
