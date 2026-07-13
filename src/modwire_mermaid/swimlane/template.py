from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import ClassVar

from ..graph import ModwireFlowchartStyleProperty
from ..graph_rendering import ModwireFlowchartRendering
from ..style_rendering import MermaidStyleRendering
from ..template import JinjaDiagramTemplate
from .diagram import ModwireSwimlaneDiagram


def _style_property(value: ModwireFlowchartStyleProperty) -> str:
    return MermaidStyleRendering.property(value.name, value.value)


class ModwireSwimlaneTemplate(JinjaDiagramTemplate[ModwireSwimlaneDiagram]):
    package = "modwire_mermaid.swimlane"
    name = "diagram.j2"
    filters: ClassVar[Mapping[str, Callable[..., object]]] = MappingProxyType(
        {
            "flow_node": ModwireFlowchartRendering.node,
            "flow_edge": ModwireFlowchartRendering.edge,
            "style_property": _style_property,
        }
    )
