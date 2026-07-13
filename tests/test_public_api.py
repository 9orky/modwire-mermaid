import modwire_mermaid
from modwire_mermaid import CompilerRegistry, DiagramCompiler, MermaidDiagram
from modwire_mermaid.timeline import ModwireTimeline, ModwireTimelineBuilder, ModwireTimelineCompiler


def test_root_api_exposes_cross_cutting_v2_contracts():
    assert modwire_mermaid.__all__ == [
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
    ]


def test_feature_packages_are_the_supported_import_surface():
    assert ModwireTimeline.model_fields["kind"].default == "timeline"
    assert ModwireTimelineBuilder is not None
    assert ModwireTimelineCompiler is not None
    assert CompilerRegistry is not None and DiagramCompiler is not None and MermaidDiagram is not None
