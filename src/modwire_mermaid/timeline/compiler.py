from ..compiler import DiagramCompiler
from ..template import DiagramTemplate
from .diagram import ModwireTimeline


class ModwireTimelineCompiler(DiagramCompiler[ModwireTimeline]):
    def __init__(self, template: DiagramTemplate[ModwireTimeline]):
        self._template = template

    @property
    def diagram_type(self) -> type[ModwireTimeline]:
        return ModwireTimeline

    def compile(self, diagram: ModwireTimeline) -> str:
        return self._template.render(diagram)
