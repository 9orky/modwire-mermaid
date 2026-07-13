from typing import Literal

from pydantic import Field, model_validator

from ..contracts import (
    ModwireBaseDiagram,
    ModwireContractViolation,
    ModwireDiagramContract,
    ModwireSyntaxFeature,
    ModwireText,
    contract_validation_error,
)


class ModwireUserJourneyTask(ModwireDiagramContract):
    name: ModwireText
    score: int = Field(ge=1, le=5)
    actors: tuple[ModwireText, ...] = ()


class ModwireUserJourneySection(ModwireDiagramContract):
    name: ModwireText
    tasks: tuple[ModwireUserJourneyTask, ...]


class ModwireUserJourney(ModwireBaseDiagram):
    kind: Literal["user-journey"] = "user-journey"
    docs_url = "https://mermaid.js.org/syntax/userJourney.html"
    syntax_features = (ModwireSyntaxFeature("syntax", "test_user_journey_compiles_sections_scores_and_actors"),)

    title: ModwireText
    sections: tuple[ModwireUserJourneySection, ...]

    @model_validator(mode="after")
    def validate_journey(self):
        self._require_children(self.sections, "User journey")
        violations = tuple(
            ModwireContractViolation(
                ("sections", index, "tasks"),
                "missing_child",
                "Every user-journey section must contain a task",
                section.tasks,
            )
            for index, section in enumerate(self.sections)
            if not section.tasks
        )
        if violations:
            raise contract_validation_error(type(self).__name__, violations)
        return self
