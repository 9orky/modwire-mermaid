from modwire_mermaid.composition import ModwireMermaidFactory
from modwire_mermaid.timeline.diagram import ModwireTimelineBuilder

diagram = (
    ModwireTimelineBuilder.create("Release history")
    .section("2026")
    .period("Q1", "Private beta")
    .period("Q2", "Public release", "Documentation")
    .build()
)

source = ModwireMermaidFactory.standard().compile(diagram)
