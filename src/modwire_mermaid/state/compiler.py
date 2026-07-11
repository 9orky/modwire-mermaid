from ..compiler import DiagramCompiler
from ..template import DiagramTemplate
from .diagram import ModwireStateDiagram


class ModwireStateCompiler(DiagramCompiler[ModwireStateDiagram]):
    def __init__(self, template: DiagramTemplate[ModwireStateDiagram]):
        self._template = template

    @property
    def diagram_type(self) -> type[ModwireStateDiagram]:
        return ModwireStateDiagram

    def compile(self, diagram: ModwireStateDiagram) -> str:
        return self._template.render(diagram)
