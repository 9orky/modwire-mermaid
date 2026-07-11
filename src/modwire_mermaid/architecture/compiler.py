from ..compiler import DiagramCompiler
from ..template import DiagramTemplate
from .diagram import ModwireArchitectureDiagram


class ModwireArchitectureCompiler(DiagramCompiler[ModwireArchitectureDiagram]):
    def __init__(self, template: DiagramTemplate[ModwireArchitectureDiagram]):
        self._template = template

    @property
    def diagram_type(self) -> type[ModwireArchitectureDiagram]:
        return ModwireArchitectureDiagram

    def compile(self, diagram: ModwireArchitectureDiagram) -> str:
        return self._template.render(diagram)
