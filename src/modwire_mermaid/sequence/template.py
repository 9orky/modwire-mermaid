from ..template import JinjaDiagramTemplate
from .diagram import ModwireSequenceDiagram


class ModwireSequenceTemplate(JinjaDiagramTemplate[ModwireSequenceDiagram]):
    package = "modwire_mermaid.sequence"
    name = "diagram.j2"
