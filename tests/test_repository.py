import runpy
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_documented_example_executes():
    namespace = runpy.run_path(ROOT / "examples/compile_timeline.py")
    assert "timeline LR\n" in namespace["source"]


def test_release_uses_trusted_publishing_without_secrets():
    source = (ROOT / ".github/workflows/release.yml").read_text()
    publish = source.split("  publish-pypi:", 1)[1].split("  github-release:", 1)[0]
    assert "environment:\n      name: pypi" in publish
    assert "permissions:\n      id-token: write" in publish
    assert "pypa/gh-action-pypi-publish@release/v1" in publish
    assert "password:" not in publish and "secrets." not in publish


def test_readme_documents_non_null_absence_defaults_and_explicit_imports():
    source = (ROOT / "README.md").read_text()

    assert "Omitted optional text and references use typed, non-null" in source
    assert "empty-string defaults; explicit `None` is rejected" in source
    assert "Optional values use `None`" not in source
    assert "from modwire_mermaid import" not in source
