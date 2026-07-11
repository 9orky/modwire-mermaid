from collections.abc import Mapping
from types import MappingProxyType
from typing import ClassVar

from ..flowchart.rendering import ModwireFlowchartRendering
from ..template import JinjaDiagramTemplate
from .diagram import ModwireSwimlaneDiagram


class ModwireSwimlaneTemplate(JinjaDiagramTemplate[ModwireSwimlaneDiagram]):
    package = "modwire_mermaid.swimlane"
    name = "diagram.j2"
    filters: ClassVar[Mapping[str, object]] = MappingProxyType(
        {
            "flow_node": ModwireFlowchartRendering.node,
            "flow_edge": ModwireFlowchartRendering.edge,
        }
    )
