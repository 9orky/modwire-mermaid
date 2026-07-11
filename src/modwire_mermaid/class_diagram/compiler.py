from ..compiler import DiagramCompiler
from .diagram import ModwireClassDiagram
from .template import ModwireClassDiagramTemplate


class ModwireClassDiagramCompiler(DiagramCompiler[ModwireClassDiagram]):
    def __init__(self, template: ModwireClassDiagramTemplate):
        self._template = template

    @property
    def diagram_type(self) -> type[ModwireClassDiagram]:
        return ModwireClassDiagram

    def compile(self, diagram: ModwireClassDiagram) -> str:
        return self._template.render(diagram)
