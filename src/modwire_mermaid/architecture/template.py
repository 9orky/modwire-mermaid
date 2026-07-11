from ..template import JinjaDiagramTemplate
from .diagram import ModwireArchitectureDiagram


class ModwireArchitectureTemplate(JinjaDiagramTemplate[ModwireArchitectureDiagram]):
    package = "modwire_mermaid.architecture"
    name = "diagram.j2"
