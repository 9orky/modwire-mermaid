from ._version import __version__
from .compiler import DiagramCompiler
from .composition import ModwireMermaidFactory
from .contracts import (
    CompilerRegistrationError,
    DiagramBuilder,
    DiagramBuildError,
    DiagramCompilationError,
    DuplicateCompilerError,
    MermaidDiagram,
    ModwireBaseDiagram,
    ModwireDiagramContract,
    ModwireMermaidError,
    UnsupportedDiagramError,
)
from .diagrams import Diagram, DiagramAdapter
from .facade import ModwireMermaid
from .registry import CompilerRegistry
from .schema import DIAGRAM_SCHEMA_VERSION, diagram_json_schema

__all__ = [
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
