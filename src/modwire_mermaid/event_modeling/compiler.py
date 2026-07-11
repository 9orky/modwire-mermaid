from ..compiler import DiagramCompiler
from ..template import DiagramTemplate
from .diagram import ModwireEventModel


class ModwireEventModelCompiler(DiagramCompiler[ModwireEventModel]):
    def __init__(self, template: DiagramTemplate[ModwireEventModel]):
        self._template = template

    @property
    def diagram_type(self) -> type[ModwireEventModel]:
        return ModwireEventModel

    def compile(self, diagram: ModwireEventModel) -> str:
        return self._template.render(diagram)
