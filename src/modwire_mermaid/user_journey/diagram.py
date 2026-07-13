from typing import Literal

from pydantic import Field, model_validator

from ..contracts import ModwireBaseDiagram, ModwireDiagramContract, ModwireSyntaxFeature


class ModwireUserJourneyTask(ModwireDiagramContract):
    name: str
    score: int = Field(ge=1, le=5)
    actors: tuple[str, ...]


class ModwireUserJourneySection(ModwireDiagramContract):
    name: str
    tasks: tuple[ModwireUserJourneyTask, ...]


class ModwireUserJourney(ModwireBaseDiagram):
    kind: Literal["user-journey"] = "user-journey"
    docs_url = "https://mermaid.js.org/syntax/userJourney.html"
    syntax_features = (ModwireSyntaxFeature("syntax", "test_user_journey_compiles_sections_scores_and_actors"),)

    title: str
    sections: tuple[ModwireUserJourneySection, ...]

    @model_validator(mode="after")
    def validate_journey(self):
        self._require_children(self.sections, "User journey")
        if any(not section.tasks for section in self.sections):
            raise ValueError("Every user-journey section must contain a task")
        return self
