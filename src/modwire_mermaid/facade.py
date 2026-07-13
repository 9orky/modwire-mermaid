from .contracts import MermaidDiagram
from .registry import CompilerRegistry


class ModwireMermaid:
    """Compile validated diagram contracts into deterministic Mermaid source."""

    def __init__(self, registry: CompilerRegistry):
        self._registry = registry

    @property
    def registry(self) -> CompilerRegistry:
        return self._registry

    def compile(self, diagram: MermaidDiagram) -> str:
        return self._registry.compile(diagram)
