from ..compiler import DiagramCompiler
from ..template import DiagramTemplate
from .diagram import ModwireSwimlaneDiagram


class ModwireSwimlaneCompiler(DiagramCompiler[ModwireSwimlaneDiagram]):
    def __init__(self, template: DiagramTemplate[ModwireSwimlaneDiagram]):
        self._template = template

    @property
    def diagram_type(self) -> type[ModwireSwimlaneDiagram]:
        return ModwireSwimlaneDiagram

    def compile(self, diagram: ModwireSwimlaneDiagram) -> str:
        return self._template.render(diagram)
