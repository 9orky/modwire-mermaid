from .contracts import ModwireBaseDiagram
from .registry import DiagramCompilerRegistry


class ModwireMermaid:
    """Compile validated Modwire diagram contracts into deterministic Mermaid source."""

    def __init__(self, registry: DiagramCompilerRegistry):
        self._registry = registry

    def compile(self, diagram: ModwireBaseDiagram) -> str:
        """Compile one supported diagram contract into Mermaid text."""
        return self._registry.compiler_for(diagram).compile_diagram(diagram)
