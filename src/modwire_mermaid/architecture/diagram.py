from enum import StrEnum
from typing import Literal

from pydantic import model_validator

from ..contracts import ModwireBaseDiagram, ModwireDiagramContract, ModwireDiagramIdentifier, ModwireSyntaxFeature


class ModwireArchitectureSide(StrEnum):
    LEFT = "L"
    RIGHT = "R"
    TOP = "T"
    BOTTOM = "B"


class ModwireArchitectureGroup(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    icon: str | None = None
    label: str | None = None
    parent_id: ModwireDiagramIdentifier | None = None


class ModwireArchitectureService(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    icon: str | None = None
    label: str | None = None
    group_id: ModwireDiagramIdentifier | None = None


class ModwireArchitectureJunction(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    group_id: ModwireDiagramIdentifier | None = None


class ModwireArchitectureEdge(ModwireDiagramContract):
    source: ModwireDiagramIdentifier
    source_side: ModwireArchitectureSide
    source_group_edge: bool
    target: ModwireDiagramIdentifier
    target_side: ModwireArchitectureSide
    target_group_edge: bool
    bidirectional: bool


class ModwireArchitectureDiagram(ModwireBaseDiagram):
    kind: Literal["architecture"] = "architecture"
    docs_url = "https://mermaid.js.org/syntax/architecture.html"
    syntax_features = (
        ModwireSyntaxFeature("edges", "test_architecture_supports_junctions_and_group_edges"),
        ModwireSyntaxFeature("groups", "test_architecture_supports_junctions_and_group_edges"),
        ModwireSyntaxFeature("junctions", "test_architecture_supports_junctions_and_group_edges"),
        ModwireSyntaxFeature("services", "test_architecture_supports_junctions_and_group_edges"),
    )

    services: tuple[ModwireArchitectureService, ...]
    groups: tuple[ModwireArchitectureGroup, ...] = ()
    junctions: tuple[ModwireArchitectureJunction, ...] = ()
    edges: tuple[ModwireArchitectureEdge, ...] = ()
    title: str | None = None

    @model_validator(mode="after")
    def validate_architecture(self):
        self._require_children(self.services, "Architecture diagram")
        group_ids = tuple(item.id for item in self.groups)
        service_ids = tuple(item.id for item in self.services)
        junction_ids = tuple(item.id for item in self.junctions)
        self._validate_unique_children(group_ids, "Architecture groups")
        self._validate_unique_children(service_ids, "Architecture services")
        self._validate_unique_children(junction_ids, "Architecture junctions")
        self._validate_unique_children((*service_ids, *junction_ids), "Architecture nodes")
        self._validate_child_references(
            group_ids, (item.group_id for item in self.services if item.group_id), "Architecture group"
        )
        self._validate_child_references(
            group_ids, (item.parent_id for item in self.groups if item.parent_id), "Architecture parent"
        )
        self._validate_child_references(
            group_ids, (item.group_id for item in self.junctions if item.group_id), "Architecture junction group"
        )
        self._validate_child_references(
            (*service_ids, *junction_ids),
            (value for edge in self.edges for value in (edge.source, edge.target)),
            "Architecture node",
        )
        parents = {item.id: item.parent_id for item in self.groups}
        for group_id in group_ids:
            visited: set[str] = set()
            current: str | None = group_id
            while current is not None:
                if current in visited:
                    raise ValueError(f"Architecture group hierarchy contains a cycle at {current!r}")
                visited.add(current)
                current = parents.get(current)
        service_groups = {item.id: item.group_id for item in self.services}
        for edge in self.edges:
            if edge.source_group_edge and not service_groups.get(edge.source):
                raise ValueError("Architecture source group edges require a grouped service")
            if edge.target_group_edge and not service_groups.get(edge.target):
                raise ValueError("Architecture target group edges require a grouped service")
        return self
