from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import ClassVar

from ..template import DiagramTemplate, JinjaDiagramTemplate
from .diagram import ModwireClassDiagram
from .rendering import ModwireClassRendering


class ModwireClassDiagramTemplate(DiagramTemplate[ModwireClassDiagram]):
    pass


class JinjaClassDiagramTemplate(
    JinjaDiagramTemplate[ModwireClassDiagram],
    ModwireClassDiagramTemplate,
):
    package = "modwire_mermaid.class_diagram"
    name = "diagram.j2"
    filters: ClassVar[Mapping[str, Callable[..., object]]] = MappingProxyType(
        {
            "class_member": ModwireClassRendering.member,
            "relationship_arrow": ModwireClassRendering.relationship_arrow,
            "style_property": ModwireClassRendering.style_property,
        }
    )
