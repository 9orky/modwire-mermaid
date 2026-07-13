from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Support = Literal["supported", "partial", "unsupported"]


@dataclass(frozen=True, slots=True)
class FeatureClaim:
    slug: str
    status: Support
    reason: str
    evidence: tuple[str, ...] = ()


def supported(slug: str, *evidence: str) -> FeatureClaim:
    return FeatureClaim(slug, "supported", "Emitted by the typed model and exercised by the corpus.", evidence)


INVENTORY: dict[str, tuple[FeatureClaim, ...]] = {
    "architecture": (
        supported("services", "architecture.minimal", "architecture.comprehensive"),
        supported("groups", "architecture.comprehensive"),
        supported("junctions", "architecture.comprehensive"),
        supported("edges", "architecture.comprehensive"),
        FeatureClaim("service-alignment", "unsupported", "Mermaid row/column alignment has no typed field."),
        FeatureClaim("architecture-configuration", "unsupported", "Architecture configuration is not modeled."),
    ),
    "class": (
        supported("classes-members-generics-annotations", "class.comprehensive"),
        supported("namespaces-relationships-notes", "class.comprehensive"),
        supported("interactions-styles-configuration", "class.comprehensive"),
        FeatureClaim("alternate-member-authoring", "unsupported", "One canonical typed authoring form is emitted."),
    ),
    "event-modeling": (
        supported("entity-types-and-timeline", "event-modeling.minimal", "event-modeling.comprehensive"),
        supported("reset-relations-inline-data-data-blocks-namespaces", "event-modeling.comprehensive"),
    ),
    "file-tree": (
        supported("recursive-tree-syntax", "file-tree.minimal", "file-tree.comprehensive"),
        supported("descriptions-icons-classes-comments-theme-configuration", "file-tree.comprehensive"),
    ),
    "flowchart": (
        supported("nodes-shapes-icons-images-markdown", "flowchart.comprehensive"),
        supported("edges-animation-curves-subgraphs-interactions-styles", "flowchart.comprehensive"),
        FeatureClaim(
            "diagram-configuration", "partial", "Typed direction and curves exist; arbitrary init config does not."
        ),
        FeatureClaim("accessibility", "unsupported", "Flowchart accessibility directives are not exposed."),
        FeatureClaim("alternate-link-authoring", "unsupported", "One canonical typed edge form is emitted."),
    ),
    "mindmap": (
        supported("shapes-markdown-icons-classes-layout", "mindmap.comprehensive"),
        supported("recursive-unicode-content", "mindmap.focused-recursive-unicode"),
    ),
    "sequence": (
        supported("participants-messages-arrow-types", "sequence.minimal", "sequence.comprehensive"),
        supported("activation-lifecycle-notes-links-boxes-rects-blocks", "sequence.comprehensive"),
        supported("boolean-autonumber", "sequence.comprehensive"),
        FeatureClaim(
            "autonumber-start-and-increment", "unsupported", "Only the boolean autonumber directive is modeled."
        ),
    ),
    "state": (
        supported("states-transitions-start-end", "state.minimal", "state.comprehensive"),
        supported("choice-fork-join-composites-concurrency-direction", "state.comprehensive"),
        supported("notes-styles-accessibility", "state.comprehensive"),
    ),
    "swimlane": (
        supported("lanes-cross-lane-edges", "swimlane.minimal", "swimlane.comprehensive"),
        supported("flowchart-nodes-icons-images-markdown-styles-interactions", "swimlane.focused-flowchart-reuse"),
        FeatureClaim("stability", "partial", "Mermaid documents swimlane syntax as experimental/beta in 11.16.0."),
    ),
    "timeline": (
        supported("title-sections-periods-events", "timeline.minimal", "timeline.comprehensive"),
        supported("directions-and-configuration", "timeline.comprehensive"),
    ),
    "user-journey": (supported("sections-tasks-scores-actors", "user-journey.minimal", "user-journey.comprehensive"),),
}
