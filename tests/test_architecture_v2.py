import ast
from pathlib import Path

PACKAGE = Path(__file__).parents[1] / "src" / "modwire_mermaid"
FEATURES = {
    "architecture",
    "class_diagram",
    "event_modeling",
    "file_tree",
    "flowchart",
    "mindmap",
    "sequence",
    "state",
    "swimlane",
    "timeline",
    "user_journey",
}


def test_diagram_features_never_import_sibling_features():
    violations: list[str] = []
    for feature in sorted(FEATURES):
        for source_path in (PACKAGE / feature).glob("*.py"):
            tree = ast.parse(source_path.read_text(), filename=str(source_path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom) or node.module is None:
                    continue
                imported = node.module.split(".")[0]
                if imported in FEATURES - {feature}:
                    violations.append(f"{source_path.relative_to(PACKAGE)} imports {node.module}")
    assert violations == []


def test_shared_foundation_never_imports_diagram_features():
    shared = (
        "compiler.py",
        "contracts.py",
        "facade.py",
        "graph.py",
        "graph_rendering.py",
        "registry.py",
        "source.py",
        "syntax.py",
        "template.py",
    )
    violations: list[str] = []
    for filename in shared:
        source_path = PACKAGE / filename
        tree = ast.parse(source_path.read_text(), filename=str(source_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] in FEATURES:
                violations.append(f"{filename} imports {node.module}")
    assert violations == []
