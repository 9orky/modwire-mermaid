from typing import Annotated

from pydantic import Field, TypeAdapter

from .architecture.diagram import ModwireArchitectureDiagram
from .class_diagram.diagram import ModwireClassDiagram
from .event_modeling import ModwireEventModel
from .file_tree import ModwireFileTree
from .graph import ModwireFlowchart
from .mindmap import ModwireMindmap
from .sequence.diagram import ModwireSequenceDiagram
from .state.diagram import ModwireStateDiagram
from .swimlane.diagram import ModwireSwimlaneDiagram
from .timeline.diagram import ModwireTimeline
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
