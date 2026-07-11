from ..compiler import DiagramCompiler
from ..template import DiagramTemplate
from .diagram import ModwireUserJourney


class ModwireUserJourneyCompiler(DiagramCompiler[ModwireUserJourney]):
    def __init__(self, template: DiagramTemplate[ModwireUserJourney]):
        self._template = template

    @property
    def diagram_type(self) -> type[ModwireUserJourney]:
        return ModwireUserJourney

    def compile(self, diagram: ModwireUserJourney) -> str:
        return self._template.render(diagram)
