# modwire-mermaid

Typed, frozen, deterministic Mermaid text diagrams behind one class-based API. The package returns
validated Mermaid source and performs no filesystem, browser, CLI, or image-rendering work.

Compilation is package-native. It does not depend on Node.js or `mermaid-py`; consumers may pass the
generated source to their preferred Mermaid renderer or validation binary.

<!-- generated:public-api:start -->
## Public API

The supported root imports below are generated from `modwire_mermaid.__all__`.

| Symbol | Purpose | Primary API |
| --- | --- | --- |
| `ModwireDiagramError` | Report an invalid diagram contract or unsupported diagram operation. | — |
| `ModwireMermaid` | Compile validated Modwire diagram contracts into deterministic Mermaid source. | `compile(diagram: modwire_mermaid.contracts.ModwireBaseDiagram) -> str` |
| `ModwireMermaidFactory` | Build the standard Mermaid façade with every bundled diagram compiler. | `standard() -> modwire_mermaid.facade.ModwireMermaid` |
| `__version__` | Installed distribution version. | — |

## Executable example

Source: [`compile_timeline.py`](examples/compile_timeline.py). This file is executed by the test suite.

```python
from modwire_mermaid import ModwireMermaidFactory
from modwire_mermaid.timeline.diagram import ModwireTimelineBuilder

diagram = (
    ModwireTimelineBuilder.create("Release history")
    .section("2026")
    .period("Q1", "Private beta")
    .period("Q2", "Public release", "Documentation")
    .build()
)

source = ModwireMermaidFactory.standard().compile(diagram)
```
<!-- generated:public-api:end -->

## Diagrams

- [Architecture](docs/architecture/README.md)
- [Class diagram](docs/class-diagram/README.md)
- [Event modeling](docs/event-modeling/README.md)
- [File tree](docs/file-tree/README.md)
- [Flowchart](docs/flowchart/README.md)
- [Mindmap](docs/mindmap/README.md)
- [Sequence diagram](docs/sequence/README.md)
- [State diagram](docs/state/README.md)
- [Swimlanes](docs/swimlanes/README.md)
- [Timeline](docs/timeline/README.md)
- [User journey](docs/user-journey/README.md)

All contracts inherit `ModwireBaseDiagram`. It enforces required children, unique child identities,
and valid references consistently. Empty strings and tuples explicitly represent Mermaid features
that are absent; public contracts are non-nullable and have no implicit defaults.

## Development and release

Run `uv sync --all-groups` and `make verify`. Releases use strict SemVer tags and PyPI Trusted
Publishing configured for repository `9orky/modwire-mermaid`, workflow `release.yml`, and environment
`pypi`.
