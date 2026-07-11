from ..template import JinjaDiagramTemplate
from .diagram import ModwireUserJourney


class ModwireUserJourneyTemplate(JinjaDiagramTemplate[ModwireUserJourney]):
    package = "modwire_mermaid.user_journey"
    name = "diagram.j2"
