from typing import Annotated

from pydantic import Field, TypeAdapter

from .architecture import ModwireArchitectureDiagram
from .class_diagram import ModwireClassDiagram
from .event_modeling import ModwireEventModel
from .file_tree import ModwireFileTree
from .flowchart import ModwireFlowchart
from .mindmap import ModwireMindmap
from .sequence import ModwireSequenceDiagram
from .state import ModwireStateDiagram
from .swimlane import ModwireSwimlaneDiagram
from .timeline import ModwireTimeline
from .user_journey import ModwireUserJourney

Diagram = Annotated[
    ModwireArchitectureDiagram
    | ModwireClassDiagram
    | ModwireEventModel
    | ModwireFileTree
    | ModwireFlowchart
    | ModwireMindmap
    | ModwireSequenceDiagram
    | ModwireStateDiagram
    | ModwireSwimlaneDiagram
    | ModwireTimeline
    | ModwireUserJourney,
    Field(discriminator="kind"),
]

DiagramAdapter: TypeAdapter[Diagram] = TypeAdapter(Diagram)

__all__ = ["Diagram", "DiagramAdapter"]
