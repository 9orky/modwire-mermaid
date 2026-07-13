import argparse
import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parents[1]
START = "<!-- generated:public-api:start -->"
END = "<!-- generated:public-api:end -->"


@dataclass(frozen=True)
class PublicSymbol:
    module: str

    name: str


@dataclass(frozen=True)
class PackageDocumentation:
    readme: Path
    example: Path
    symbols: tuple[PublicSymbol, ...]


PACKAGES = (
    PackageDocumentation(
        ROOT / "README.md",
        ROOT / "examples/compile_timeline.py",
        (
            PublicSymbol("modwire_mermaid._version", "__version__"),
            PublicSymbol("modwire_mermaid.compiler", "DiagramCompiler"),
            PublicSymbol("modwire_mermaid.composition", "ModwireMermaidFactory"),
            PublicSymbol("modwire_mermaid.contracts", "CompilerRegistrationError"),
            PublicSymbol("modwire_mermaid.contracts", "DiagramBuildError"),
            PublicSymbol("modwire_mermaid.contracts", "DiagramBuilder"),
            PublicSymbol("modwire_mermaid.contracts", "DiagramCompilationError"),
            PublicSymbol("modwire_mermaid.contracts", "DuplicateCompilerError"),
            PublicSymbol("modwire_mermaid.contracts", "MermaidDiagram"),
            PublicSymbol("modwire_mermaid.contracts", "ModwireBaseDiagram"),
            PublicSymbol("modwire_mermaid.contracts", "ModwireDiagramContract"),
            PublicSymbol("modwire_mermaid.contracts", "ModwireMermaidError"),
            PublicSymbol("modwire_mermaid.contracts", "UnsupportedDiagramError"),
            PublicSymbol("modwire_mermaid.diagrams", "Diagram"),
            PublicSymbol("modwire_mermaid.diagrams", "DiagramAdapter"),
            PublicSymbol("modwire_mermaid.facade", "ModwireMermaid"),
            PublicSymbol("modwire_mermaid.registry", "CompilerRegistry"),
            PublicSymbol("modwire_mermaid.schema", "DIAGRAM_SCHEMA_VERSION"),
            PublicSymbol("modwire_mermaid.schema", "diagram_json_schema"),
        ),
    ),
)


class DocumentationGenerator:
    @classmethod
    def render(cls, package: PackageDocumentation) -> str:
        rows = []
        for symbol in package.symbols:
            module = importlib.import_module(symbol.module)
            value = getattr(module, symbol.name)
            purpose = cls._purpose(symbol.name, value)
            operations = cls._operations(value)
            rows.append(f"| `{symbol.module}.{symbol.name}` | {purpose} | {operations} |")
        example = package.example.read_text().rstrip()
        return "\n".join(
            (
                START,
                "## Public API",
                "",
                "The supported imports below name each API's defining module; "
                "package initializers do not aggregate them.",
                "",
                "| Import path | Purpose | Primary API |",
                "| --- | --- | --- |",
                *rows,
                "",
                "## Executable example",
                "",
                f"Source: [`{package.example.name}`](examples/{package.example.name}). "
                "This file is executed by the test suite.",
                "",
                "```python",
                example,
                "```",
                END,
            )
        )

    @staticmethod
    def _purpose(name: str, value: object) -> str:
        special = {
            "DIAGRAM_SCHEMA_VERSION": "Version of the canonical bundled-diagram JSON Schema.",
            "Diagram": "Discriminated union of every bundled diagram contract.",
            "DiagramAdapter": "Validate, serialize, and publish schemas for bundled diagrams.",
            "__version__": "Installed distribution version.",
        }
        if name in special:
            return special[name]
        documentation = inspect.getdoc(value)
        if not documentation:
            raise ValueError(f"Public symbol {name} must have a docstring")
        return documentation.splitlines()[0]

    @staticmethod
    def _operations(value: object) -> str:
        if not inspect.isclass(value):
            return "—"
        operations = []
        for name, _member in value.__dict__.items():
            if name.startswith("_") or not callable(getattr(value, name, None)):
                continue
            signature = inspect.signature(getattr(value, name))
            parameters = tuple(signature.parameters.values())
            if parameters and parameters[0].name in {"self", "cls"}:
                signature = signature.replace(parameters=parameters[1:])
            operations.append(f"`{name}{signature}`")
        return "<br>".join(operations) or "—"

    @classmethod
    def update(cls, package: PackageDocumentation, check: bool) -> bool:
        current = package.readme.read_text()
        generated = cls.render(package)
        if START not in current or END not in current:
            raise ValueError(f"Missing generated documentation markers in {package.readme}")
        prefix, remainder = current.split(START, 1)
        _, suffix = remainder.split(END, 1)
        expected = f"{prefix}{generated}{suffix}"
        if current == expected:
            return True
        if not check:
            package.readme.write_text(expected)
        return False

    @classmethod
    def run(cls, check: bool) -> int:
        stale = [package.readme for package in PACKAGES if not cls.update(package, check)]
        if check and stale:
            print("Generated documentation is stale:")
            for path in stale:
                print(f"- {path.relative_to(ROOT)}")
            print("Run `make docs` and commit the result.")
            return 1
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate public API and example sections in package READMEs.")
    parser.add_argument("--check", action="store_true", help="Fail instead of updating stale documentation.")
    raise SystemExit(DocumentationGenerator.run(parser.parse_args().check))
