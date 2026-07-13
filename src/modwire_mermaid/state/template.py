from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import ClassVar

from ..style_rendering import MermaidStyleRendering
from ..template import JinjaDiagramTemplate
from .diagram import ModwireStateDiagram, ModwireStateStyleProperty


def _style_property(value: ModwireStateStyleProperty) -> str:
    return MermaidStyleRendering.property(value.name, value.value)


class ModwireStateTemplate(JinjaDiagramTemplate[ModwireStateDiagram]):
    package = "modwire_mermaid.state"
    name = "diagram.j2"
    filters: ClassVar[Mapping[str, Callable[..., object]]] = MappingProxyType({"style_property": _style_property})
