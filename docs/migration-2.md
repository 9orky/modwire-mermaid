# Migrating to modwire-mermaid 2

Version 2 intentionally removes the compatibility surface that would weaken the compiler contract.
There are no deprecated aliases or legacy constructor adapters.

| Version 1 | Version 2 |
| --- | --- |
| Feature-package barrel imports | Import contracts from `modwire_mermaid.<feature>.diagram` and compilers from `.compiler` |
| `ModwireDiagramError` for mixed concerns | Pydantic `ValidationError` for models; typed operational errors |
| ABC compiler/registry hierarchy | Structural `DiagramCompiler[T]` plus immutable `CompilerRegistry` |
| Reconstruct internal standard composition | `standard_registry()` and persistent registry operations |
| Nullable strings and references | Non-null strings with concise empty defaults for omitted text and references |
| Undiscriminated top-level models | Literal `kind` fields and the public `DiagramAdapter` |
| Flowchart-owned swimlane primitives | Shared graph contracts and rendering foundation |

Registry changes are persistent:

```python
registry = ModwireMermaidFactory.standard_registry()
extended = registry.with_compiler(CustomCompiler())
overridden = extended.replace(ReplacementCompiler())
```

`with_compiler()` rejects duplicates, `replace()` requires an existing exact diagram type, and
`without()` requires a registered type. Existing registry objects never mutate.

Model payloads must include `kind` when validated through `DiagramAdapter`. Explicit `diagram` and
`compiler` modules are the supported feature import paths; shared flowchart graph contracts live in
`modwire_mermaid.graph`. Generated Mermaid remains deterministic, but v2 does not promise
byte identity with v1 where stronger validation or canonical rendering requires a change.

## JSON Schema

`modwire_mermaid.DIAGRAM_SCHEMA_VERSION` identifies the supported schema generation contract.
Call `modwire_mermaid.diagram_json_schema()` for the canonical schema object. The deterministic packaged
artifact is `modwire_mermaid/schemas/v2/diagram.schema.json`; CI rejects drift between the artifact and models.
