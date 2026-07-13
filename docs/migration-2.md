# Migrating to modwire-mermaid 2

Version 2 intentionally removes the compatibility surface that would weaken the compiler contract.
There are no deprecated aliases or legacy constructor adapters.

| Version 1 | Version 2 |
| --- | --- |
| `modwire_mermaid.<feature>.diagram` imports | Import contracts from `modwire_mermaid.<feature>` |
| `ModwireDiagramError` for mixed concerns | Pydantic `ValidationError` for models; typed operational errors |
| ABC compiler/registry hierarchy | Structural `DiagramCompiler[T]` plus immutable `CompilerRegistry` |
| Reconstruct internal standard composition | `standard_registry()` and persistent registry operations |
| Empty strings for absent references/config | `None` for absence and typed defaults for ordinary configuration |
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

Model payloads must include `kind` when validated through `DiagramAdapter`. Feature package exports are
the supported diagram import paths. Generated Mermaid remains deterministic, but v2 does not promise
byte identity with v1 where stronger validation or canonical rendering requires a change.
