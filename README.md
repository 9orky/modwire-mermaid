# modwire-mermaid

Build [Mermaid](https://mermaid.js.org/) diagrams from typed, immutable Python objects.
`modwire-mermaid` validates a diagram's structure and compiles it to deterministic Mermaid text
behind one class-based API. It performs no filesystem, browser, CLI, or image-rendering work.

Compilation is package-native. It does not depend on Node.js or `mermaid-py`; consumers may pass the
generated source to their preferred Mermaid renderer or validation binary.

## What is Mermaid?

Mermaid is a text-based diagramming language. A short definition such as:

```mermaid
flowchart LR
    contract[Typed Python contract] --> compiler[modwire-mermaid]
    compiler --> source[Mermaid source]
    source --> renderer[Mermaid renderer]
```

can be rendered as a diagram by Mermaid-aware tools. Because the source is plain text, diagrams are
easy to review in version control, generate in tests, embed in Markdown, and render independently in
a browser or CI pipeline.

This package owns the first two steps: typed Python contracts and Mermaid source generation. Mermaid
itself—or a service or application that embeds it—owns visual rendering.

## Installation

`modwire-mermaid` requires Python 3.12 or newer.

```bash
pip install modwire-mermaid
```

## Quick start

Create a diagram with one of the feature builders, then compile it with the standard façade:

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
print(source)
```

The result is plain Mermaid source:

```text
---
config:
  timeline:
    disableMulticolor: false
---
timeline LR
  title Release history
  section 2026
    Q1 : Private beta
    Q2 : Public release : Documentation
```

Put the result inside a fenced `mermaid` block in supported Markdown, send it to the
[Mermaid Live Editor](https://mermaid.live/), or pass it to the renderer used by your application.
Rendering is deliberately outside this package, so server-side code can generate diagrams without
shipping a browser or Node.js runtime.

<!-- generated:public-api:start -->
## Public API

The supported root imports below are generated from `modwire_mermaid.__all__`.

| Symbol | Purpose | Primary API |
| --- | --- | --- |
| `DIAGRAM_SCHEMA_VERSION` | str(object='') -> str | — |
| `CompilerRegistrationError` | Report an invalid compiler registry operation. | — |
| `CompilerRegistry` | Immutable exact-type compiler registry with explicit conflict semantics. | `empty() -> 'CompilerRegistry'`<br>`with_compiler(compiler: 'DiagramCompiler[DiagramT]') -> 'CompilerRegistry'`<br>`without(diagram_type: 'type[MermaidDiagram]') -> 'CompilerRegistry'`<br>`replace(compiler: 'DiagramCompiler[DiagramT]') -> 'CompilerRegistry'`<br>`merge(other: 'CompilerRegistry') -> 'CompilerRegistry'`<br>`compile(diagram: 'MermaidDiagram') -> 'str'` |
| `Diagram` | Discriminated union of every bundled diagram contract. | — |
| `DiagramAdapter` | Validate, serialize, and publish schemas for bundled diagrams. | — |
| `DiagramBuildError` | Report invalid ordering or missing context in a diagram builder. | — |
| `DiagramBuilder` | Build one validated diagram without exposing mutable intermediate state. | `build() -> +BuiltDiagramT` |
| `DiagramCompilationError` | Wrap a selected compiler failure with stable diagram context. | — |
| `DiagramCompiler` | Compile one exact diagram type into deterministic Mermaid source. | `compile(diagram: 'DiagramT') -> 'str'` |
| `DuplicateCompilerError` | Report an attempt to register the same exact diagram type twice. | — |
| `MermaidDiagram` | Structural contract accepted by compiler registries and the façade. | — |
| `ModwireBaseDiagram` | Recommended Pydantic base for built-in and external diagrams. | — |
| `ModwireDiagramContract` | Strict frozen Pydantic base for all bundled semantic contracts. | — |
| `ModwireMermaid` | Compile validated diagram contracts into deterministic Mermaid source. | `compile(diagram: modwire_mermaid.contracts.MermaidDiagram) -> str` |
| `ModwireMermaidError` | Base class for operational modwire-mermaid failures. | — |
| `ModwireMermaidFactory` | Build the standard Mermaid façade with every bundled diagram compiler. | `standard_registry() -> modwire_mermaid.registry.CompilerRegistry`<br>`standard() -> modwire_mermaid.facade.ModwireMermaid` |
| `UnsupportedDiagramError` | Report a diagram whose exact type has no registered compiler. | — |
| `__version__` | Installed distribution version. | — |
| `diagram_json_schema` | Return the canonical versioned schema for every bundled diagram. | — |

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

Built-in contracts inherit `ModwireBaseDiagram`; extensions may use that strict Pydantic base or satisfy
the public structural compiler contract. Diagram kinds are discriminated and serializable through
`DiagramAdapter`. Required semantic roots stay explicit, while immutable empty tuples and ordinary
Mermaid configuration use typed defaults. Optional values use `None`, never magic empty-string sentinels.

## Design guarantees and scope

- Typed, frozen Pydantic contracts reject invalid diagram structure before compilation.
- Identical contracts produce identical Mermaid text, making snapshot tests and source diffs stable.
- The standard factory supports every diagram type listed above through one `compile()` method.
- The package generates text only; it does not render SVG/PNG, invoke Mermaid CLI, or write files.
- Mermaid parser and renderer compatibility must be checked by the consuming application.

## JSON Schema

`DIAGRAM_SCHEMA_VERSION` is `"2"`. Use `diagram_json_schema()` for the canonical bundled-diagram schema,
or consume the packaged `modwire_mermaid/schemas/v2/diagram.schema.json` artifact. Schema drift is checked in CI.
- Compiler registries are immutable; duplicates fail and replacement is always explicit.

## Extending the compiler

Implement `DiagramCompiler[YourDiagram]`, then compose it without mutating the standard registry:

```python
from modwire_mermaid import ModwireMermaid, ModwireMermaidFactory

registry = ModwireMermaidFactory.standard_registry().with_compiler(MyCompiler())
source = ModwireMermaid(registry).compile(MyDiagram(...))
```

Exact diagram-type dispatch is intentional. Use `replace()` when overriding an existing compiler.
See [the v2 migration guide](docs/migration-2.md) for the breaking API and model changes.

## Development and release

Run `uv sync --all-groups` and `make verify`. Releases use strict SemVer tags and PyPI Trusted
Publishing configured for repository `modwire/modwire-mermaid`, workflow `release.yml`, and environment
`pypi`. Create and push the tag before publishing its GitHub Release; that release drives the shared
build, attaches the verified distributions, and then publishes the same files to PyPI.

```sh
git tag -a v1.0.1 -m "v1.0.1"
git push origin v1.0.1
gh release create v1.0.1 --verify-tag --generate-notes --title v1.0.1
```
