from __future__ import annotations

from collections import Counter
from pathlib import Path

from pydantic import ValidationError

from compatibility.cases import CASES, INVALID_CASES
from compatibility.inventory import INVENTORY
from modwire_mermaid.composition import ModwireMermaidFactory
from modwire_mermaid.diagrams import DiagramAdapter

ROOT = Path(__file__).parents[1]
KINDS = {
    "architecture",
    "class",
    "event-modeling",
    "file-tree",
    "flowchart",
    "mindmap",
    "sequence",
    "state",
    "swimlane",
    "timeline",
    "user-journey",
}


def test_every_diagram_has_minimal_and_comprehensive_evidence() -> None:
    profiles = Counter((case.kind, case.profile) for case in CASES)
    assert set(INVENTORY) == KINDS
    assert {case.kind for case in CASES} == KINDS
    assert all(profiles[kind, "minimal"] == profiles[kind, "comprehensive"] == 1 for kind in KINDS)
    case_ids = {case.id for case in CASES}
    assert all(set(claim.evidence) <= case_ids for claims in INVENTORY.values() for claim in claims)


def test_corpus_is_typed_deterministic_and_matches_snapshots() -> None:
    compiler = ModwireMermaidFactory.standard()
    for case in CASES:
        diagram = case.factory()
        encoded = DiagramAdapter.dump_json(diagram)
        assert DiagramAdapter.dump_json(DiagramAdapter.validate_json(encoded)) == encoded
        source = compiler.compile(diagram)
        assert compiler.compile(case.factory()) == source
        assert (ROOT / "compatibility" / "snapshots" / "source" / f"{case.id}.mmd").read_text() == source


def test_invalid_cases_have_stable_diagnostics() -> None:
    for case in INVALID_CASES:
        try:
            case.factory()
        except ValidationError as error:
            first = error.errors()[0]
            assert first["type"] == case.error_type
            assert tuple(first["loc"]) == case.location
        else:
            raise AssertionError(f"Invalid fixture did not fail: {case.id}")


def test_mermaid_cli_uses_the_exact_runner_node_runtime() -> None:
    runner = (ROOT / "compatibility" / "runner.mjs").read_text()
    assert "execFileSync(" in runner
    assert "process.execPath," in runner
    assert 'node_modules", ".bin", "mmdc"' not in runner


def test_browser_sandbox_is_disabled_only_on_ci_and_shared_with_mermaid_cli() -> None:
    runner = (ROOT / "compatibility" / "runner.mjs").read_text()
    assert 'process.env.CI === "true"' in runner
    assert '["--no-sandbox", "--disable-setuid-sandbox"]' in runner
    assert '[cliEntry, "-p", puppeteerConfig' in runner
    assert 'browserSandbox: browserArgs.length === 0 ? "default" : "disabled-ci-runner"' in runner
