from ..template import JinjaDiagramTemplate
from .diagram import ModwireStateDiagram


class ModwireStateTemplate(JinjaDiagramTemplate[ModwireStateDiagram]):
    package = "modwire_mermaid.state"
    name = "diagram.j2"
