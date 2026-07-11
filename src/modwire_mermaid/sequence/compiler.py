from ..compiler import DiagramCompiler
from ..template import DiagramTemplate
from .diagram import ModwireSequenceDiagram


class ModwireSequenceCompiler(DiagramCompiler[ModwireSequenceDiagram]):
    def __init__(self, template: DiagramTemplate[ModwireSequenceDiagram]):
        self._template = template

    @property
    def diagram_type(self) -> type[ModwireSequenceDiagram]:
        return ModwireSequenceDiagram

    def compile(self, diagram: ModwireSequenceDiagram) -> str:
        return self._template.render(diagram)
