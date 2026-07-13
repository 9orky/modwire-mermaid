from typing import Annotated

from pydantic import Field, TypeAdapter

from .architecture.diagram import ModwireArchitectureDiagram
from .class_diagram.diagram import ModwireClassDiagram
from .event_modeling.diagram import ModwireEventModel
from .file_tree.diagram import ModwireFileTree
from .graph import ModwireFlowchart
from .mindmap.diagram import ModwireMindmap
from .sequence.diagram import ModwireSequenceDiagram
from .state.diagram import ModwireStateDiagram
from .swimlane.diagram import ModwireSwimlaneDiagram
from .timeline.diagram import ModwireTimeline
from .user_journey.diagram import ModwireUserJourney

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
