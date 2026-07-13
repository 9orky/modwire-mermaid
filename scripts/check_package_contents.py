import argparse
import tarfile
import zipfile
from pathlib import Path

PACKAGE = Path("modwire_mermaid")
REQUIRED_PACKAGE_PATHS = {
    PACKAGE / "py.typed",
    PACKAGE / "compiler.py",
    PACKAGE / "contracts.py",
    PACKAGE / "graph.py",
    PACKAGE / "graph_rendering.py",
    PACKAGE / "registry.py",
    PACKAGE / "schema.py",
    PACKAGE / "source.py",
    PACKAGE / "style_rendering.py",
    PACKAGE / "syntax.py",
    PACKAGE / "template.py",
    PACKAGE / "schemas/v2/diagram.schema.json",
    *(
        PACKAGE / feature / "diagram.j2"
        for feature in (
            "architecture",
            "class_diagram",
            "event_modeling",
            "sequence",
            "state",
            "swimlane",
            "timeline",
            "user_journey",
        )
    ),
}
REQUIRED_SDIST_PATHS = {
    Path(".node-version"),
    Path("compatibility/catalog.json"),
    Path("compatibility/runner.mjs"),
    Path("compatibility/toolchains/minimum/package-lock.json"),
    Path("compatibility/toolchains/latest-11/package-lock.json"),
    Path("compatibility/snapshots/source/architecture.minimal.mmd"),
    Path("compatibility/snapshots/source/swimlane.comprehensive.mmd"),
    Path("docs/architecture/compatibility.md"),
    Path("docs/swimlanes/compatibility.md"),
    Path("scripts/generate_compatibility.py"),
}


def _wheel_paths(path: Path) -> set[Path]:
    with zipfile.ZipFile(path) as archive:
        return {Path(name) for name in archive.namelist()}


def _sdist_paths(path: Path) -> set[Path]:
    with tarfile.open(path, mode="r:gz") as archive:
        return {Path(*Path(name).parts[1:]) for name in archive.getnames() if len(Path(name).parts) > 1}


def _assert_contents(kind: str, paths: set[Path]) -> None:
    package_paths = (
        paths if kind == "wheel" else {path.relative_to("src") for path in paths if path.parts[:1] == ("src",)}
    )
    missing = sorted(REQUIRED_PACKAGE_PATHS - package_paths)
    if missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise SystemExit(f"{kind} is missing required package content:\n{formatted}")
    if kind == "sdist":
        missing_sdist = sorted(REQUIRED_SDIST_PATHS - paths)
        if missing_sdist:
            formatted = "\n".join(f"- {path}" for path in missing_sdist)
            raise SystemExit(f"sdist is missing compatibility evidence:\n{formatted}")
    if kind == "wheel":
        unexpected = sorted(path for path in paths if path.parts[:1] in {("compatibility",), ("docs",), ("scripts",)})
        if unexpected:
            formatted = "\n".join(f"- {path}" for path in unexpected)
            raise SystemExit(f"wheel contains repository-only compatibility evidence:\n{formatted}")
    forbidden = sorted(
        path
        for path in paths
        if "node_modules" in path.parts or path.suffix == ".svg" or ".compatibility-artifacts" in path.parts
    )
    if forbidden:
        formatted = "\n".join(f"- {path}" for path in forbidden)
        raise SystemExit(f"{kind} contains forbidden generated runtime artifacts:\n{formatted}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dist", type=Path)
    arguments = parser.parse_args()
    wheels = sorted(arguments.dist.glob("*.whl"))
    sdists = sorted(arguments.dist.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise SystemExit("Expected exactly one wheel and one sdist")
    _assert_contents("wheel", _wheel_paths(wheels[0]))
    _assert_contents("sdist", _sdist_paths(sdists[0]))


if __name__ == "__main__":
    main()
