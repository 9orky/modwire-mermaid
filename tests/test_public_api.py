import modwire_mermaid
from modwire_mermaid._version import __version__
from modwire_mermaid.compiler import DiagramCompiler
from modwire_mermaid.composition import ModwireMermaidFactory
from modwire_mermaid.contracts import MermaidDiagram
from modwire_mermaid.diagrams import DiagramAdapter
from modwire_mermaid.facade import ModwireMermaid
from modwire_mermaid.registry import CompilerRegistry
from modwire_mermaid.schema import DIAGRAM_SCHEMA_VERSION, diagram_json_schema
from modwire_mermaid.timeline.compiler import ModwireTimelineCompiler
from modwire_mermaid.timeline.diagram import ModwireTimeline, ModwireTimelineBuilder


def test_root_initializer_does_not_create_convenience_exports():
    forbidden = {
        "CompilerRegistry",
        "DIAGRAM_SCHEMA_VERSION",
        "DiagramAdapter",
        "DiagramCompiler",
        "MermaidDiagram",
        "ModwireMermaid",
        "ModwireMermaidFactory",
        "__version__",
        "diagram_json_schema",
    }

    assert not hasattr(modwire_mermaid, "__all__")
    assert forbidden.isdisjoint(vars(modwire_mermaid))


def test_explicit_modules_are_the_supported_import_surface():
    assert ModwireTimeline.model_fields["kind"].default == "timeline"
    assert DIAGRAM_SCHEMA_VERSION == "2"
    assert diagram_json_schema()["discriminator"]["propertyName"] == "kind"
    assert __version__
    assert all(
        value is not None
        for value in (
            CompilerRegistry,
            DiagramAdapter,
            DiagramCompiler,
            MermaidDiagram,
            ModwireMermaid,
            ModwireMermaidFactory,
            ModwireTimelineBuilder,
            ModwireTimelineCompiler,
        )
    )


def test_feature_packages_do_not_create_barrel_exports():
    import modwire_mermaid.timeline as timeline

    assert not hasattr(timeline, "ModwireTimeline")
    assert not hasattr(timeline, "ModwireTimelineBuilder")
    assert not hasattr(timeline, "ModwireTimelineCompiler")
