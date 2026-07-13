from modwire_mermaid.architecture.diagram import ModwireArchitectureDiagram
from modwire_mermaid.class_diagram.diagram import ModwireClassDiagram
from modwire_mermaid.documentation import MermaidDocumentationOutlineParser
from modwire_mermaid.event_modeling import ModwireEventModel
from modwire_mermaid.file_tree import ModwireFileTree
from modwire_mermaid.graph import ModwireFlowchart
from modwire_mermaid.mindmap import ModwireMindmap
from modwire_mermaid.sequence.diagram import ModwireSequenceDiagram
from modwire_mermaid.state.diagram import ModwireStateDiagram
from modwire_mermaid.swimlane.diagram import ModwireSwimlaneDiagram
from modwire_mermaid.timeline.diagram import ModwireTimeline
from modwire_mermaid.user_journey import ModwireUserJourney

DIAGRAM_TYPES = (
    ModwireArchitectureDiagram,
    ModwireClassDiagram,
    ModwireEventModel,
    ModwireFileTree,
    ModwireFlowchart,
    ModwireMindmap,
    ModwireSequenceDiagram,
    ModwireStateDiagram,
    ModwireSwimlaneDiagram,
    ModwireTimeline,
    ModwireUserJourney,
)


def test_every_diagram_declares_documentation_and_implemented_features():
    assert all(diagram_type.docs_url.startswith("https://mermaid.js.org/syntax/") for diagram_type in DIAGRAM_TYPES)
    assert all(diagram_type.syntax_features for diagram_type in DIAGRAM_TYPES)


def test_every_declared_feature_is_linked_to_a_collected_evidence_test(request):
    collected_tests = {item.name for item in request.session.items}
    missing = {
        f"{diagram_type.__name__}.{feature.docs_slug}: {feature.evidence_test}"
        for diagram_type in DIAGRAM_TYPES
        for feature in diagram_type.syntax_features
        if feature.evidence_test not in collected_tests
    }

    assert missing == set()


def test_outline_parser_prefers_on_this_page_navigation():
    html = """
    <h2 id="fallback">Fallback</h2>
    <nav aria-labelledby="doc-outline-aria-label">
      <a href="#syntax">Syntax</a><a href="#notes">Notes and comments</a>
    </nav>
    """

    assert MermaidDocumentationOutlineParser.extract(html) == ("Syntax", "Notes and comments")


def test_outline_parser_falls_back_to_static_document_headings():
    html = '<main><h2 id="syntax">Syntax</h2><h3 id="notes">Notes</h3></main>'

    assert MermaidDocumentationOutlineParser.extract(html) == ("Syntax", "Notes")
