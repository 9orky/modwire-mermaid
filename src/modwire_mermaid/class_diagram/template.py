from ..template import DiagramTemplate, JinjaDiagramTemplate
from .diagram import ModwireClassDiagram


class ModwireClassDiagramTemplate(DiagramTemplate[ModwireClassDiagram]):
    pass


class JinjaClassDiagramTemplate(
    JinjaDiagramTemplate[ModwireClassDiagram],
    ModwireClassDiagramTemplate,
):
    package = "modwire_mermaid.class_diagram"
    name = "diagram.j2"
