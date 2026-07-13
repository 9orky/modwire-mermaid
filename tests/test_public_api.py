import modwire_mermaid
from modwire_mermaid import CompilerRegistry, DiagramCompiler, MermaidDiagram
from modwire_mermaid.timeline.compiler import ModwireTimelineCompiler
from modwire_mermaid.timeline.diagram import ModwireTimeline, ModwireTimelineBuilder


def test_root_api_exposes_cross_cutting_v2_contracts():
    assert modwire_mermaid.__all__ == [
        "DIAGRAM_SCHEMA_VERSION",
        "CompilerRegistrationError",
        "CompilerRegistry",
        "Diagram",
        "DiagramAdapter",
        "DiagramBuildError",
        "DiagramBuilder",
        "DiagramCompilationError",
        "DiagramCompiler",
        "DuplicateCompilerError",
        "MermaidDiagram",
        "ModwireBaseDiagram",
        "ModwireDiagramContract",
        "ModwireMermaid",
        "ModwireMermaidError",
        "ModwireMermaidFactory",
        "UnsupportedDiagramError",
        "__version__",
        "diagram_json_schema",
    ]


def test_explicit_feature_modules_are_the_supported_import_surface():
    assert ModwireTimeline.model_fields["kind"].default == "timeline"
    assert ModwireTimelineBuilder is not None
    assert ModwireTimelineCompiler is not None
    assert CompilerRegistry is not None and DiagramCompiler is not None and MermaidDiagram is not None


def test_feature_packages_do_not_create_barrel_exports():
    import modwire_mermaid.timeline as timeline

    assert not hasattr(timeline, "ModwireTimeline")
    assert not hasattr(timeline, "ModwireTimelineBuilder")
    assert not hasattr(timeline, "ModwireTimelineCompiler")
