from ..template import JinjaDiagramTemplate
from .diagram import ModwireEventModel


class ModwireEventModelTemplate(JinjaDiagramTemplate[ModwireEventModel]):
    package = "modwire_mermaid.event_modeling"
    name = "diagram.j2"
