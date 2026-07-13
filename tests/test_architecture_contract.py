import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
FIXTURES = ROOT / "tests" / "architecture_fixtures"


def _lint_imports(config: Path | None = None) -> subprocess.CompletedProcess[str]:
    command = [str(Path(sys.executable).with_name("lint-imports")), "--no-cache"]
    if config is not None:
        command.extend(("--config", str(config)))
    return subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)


def test_repository_dependency_contract_has_zero_baseline_violations():
    result = _lint_imports()

    assert result.returncode == 0, result.stdout + result.stderr


def test_dependency_contract_rejects_a_direct_feature_import():
    result = _lint_imports(FIXTURES / "direct.importlinter")

    assert result.returncode != 0
    assert "consumer" in result.stdout and "feature" in result.stdout


def test_dependency_contract_rejects_feature_cycles():
    result = _lint_imports(FIXTURES / "cycle.importlinter")

    assert result.returncode != 0
    assert "alpha" in result.stdout and "beta" in result.stdout
