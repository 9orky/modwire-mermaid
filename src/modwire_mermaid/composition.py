from .architecture.compiler import ModwireArchitectureCompiler
from .architecture.template import ModwireArchitectureTemplate
from .class_diagram.compiler import ModwireClassDiagramCompiler
from .class_diagram.template import JinjaClassDiagramTemplate
from .event_modeling.compiler import ModwireEventModelCompiler
from .event_modeling.template import ModwireEventModelTemplate
from .facade import ModwireMermaid
from .file_tree.compiler import ModwireFileTreeCompiler
from .flowchart.compiler import ModwireFlowchartCompiler
from .mindmap.compiler import ModwireMindmapCompiler
from .registry import CompilerRegistry
from .sequence.compiler import ModwireSequenceCompiler
from .sequence.template import ModwireSequenceTemplate
from .state.compiler import ModwireStateCompiler
from .state.template import ModwireStateTemplate
from .swimlane.compiler import ModwireSwimlaneCompiler
from .swimlane.template import ModwireSwimlaneTemplate
from .timeline.compiler import ModwireTimelineCompiler
from .timeline.template import ModwireTimelineTemplate
from .user_journey.compiler import ModwireUserJourneyCompiler
from .user_journey.template import ModwireUserJourneyTemplate


class ModwireMermaidFactory:
    """Build the standard Mermaid façade with every bundled diagram compiler."""

    @classmethod
    def standard_registry(cls) -> CompilerRegistry:
        """Return the immutable registry containing every built-in compiler."""
        mindmaps = ModwireMindmapCompiler()
        return (
            CompilerRegistry.empty()
            .with_compiler(ModwireFlowchartCompiler())
            .with_compiler(mindmaps)
            .with_compiler(ModwireFileTreeCompiler())
            .with_compiler(ModwireClassDiagramCompiler(JinjaClassDiagramTemplate.standard()))
            .with_compiler(ModwireSwimlaneCompiler(ModwireSwimlaneTemplate.standard()))
            .with_compiler(ModwireSequenceCompiler(ModwireSequenceTemplate.standard()))
            .with_compiler(ModwireStateCompiler(ModwireStateTemplate.standard()))
            .with_compiler(ModwireUserJourneyCompiler(ModwireUserJourneyTemplate.standard()))
            .with_compiler(ModwireEventModelCompiler(ModwireEventModelTemplate.standard()))
            .with_compiler(ModwireArchitectureCompiler(ModwireArchitectureTemplate.standard()))
            .with_compiler(ModwireTimelineCompiler(ModwireTimelineTemplate.standard()))
        )

    @classmethod
    def standard(cls) -> ModwireMermaid:
        """Return a ready-to-use façade for all supported diagram types."""
        return ModwireMermaid(cls.standard_registry())
