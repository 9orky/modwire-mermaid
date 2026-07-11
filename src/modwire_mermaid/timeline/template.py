from ..template import JinjaDiagramTemplate
from .diagram import ModwireTimeline


class ModwireTimelineTemplate(JinjaDiagramTemplate[ModwireTimeline]):
    package = "modwire_mermaid.timeline"
    name = "diagram.j2"
