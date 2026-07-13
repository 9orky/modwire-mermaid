from enum import StrEnum
from typing import Literal

from pydantic import model_validator

from ..contracts import (
    ModwireBaseDiagram,
    ModwireContractViolation,
    ModwireDiagramContract,
    ModwireDiagramIdentifier,
    ModwireDiagramReference,
    ModwireOptionalIconName,
    ModwireOptionalText,
    ModwireSyntaxFeature,
    contract_validation_error,
)


class ModwireArchitectureSide(StrEnum):
    LEFT = "L"
    RIGHT = "R"
    TOP = "T"
    BOTTOM = "B"


class ModwireArchitectureGroup(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    icon: ModwireOptionalIconName = ""
    label: ModwireOptionalText = ""
    parent_id: ModwireDiagramReference = ""


class ModwireArchitectureService(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    icon: ModwireOptionalIconName = ""
    label: ModwireOptionalText = ""
    group_id: ModwireDiagramReference = ""


class ModwireArchitectureJunction(ModwireDiagramContract):
    id: ModwireDiagramIdentifier
    group_id: ModwireDiagramReference = ""


class ModwireArchitectureEdge(ModwireDiagramContract):
    source: ModwireDiagramIdentifier
    source_side: ModwireArchitectureSide
    source_group_edge: bool = False
    target: ModwireDiagramIdentifier
    target_side: ModwireArchitectureSide
    target_group_edge: bool = False
    bidirectional: bool = False


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
    title: ModwireOptionalText = ""

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
        self._validate_located_references(
            group_ids,
            (
                (("services", index, "group_id"), item.group_id)
                for index, item in enumerate(self.services)
                if item.group_id
            ),
            "Architecture group",
        )
        self._validate_located_references(
            group_ids,
            (
                (("groups", index, "parent_id"), item.parent_id)
                for index, item in enumerate(self.groups)
                if item.parent_id
            ),
            "Architecture parent",
        )
        self._validate_located_references(
            group_ids,
            (
                (("junctions", index, "group_id"), item.group_id)
                for index, item in enumerate(self.junctions)
                if item.group_id
            ),
            "Architecture junction group",
        )
        self._validate_located_references(
            (*service_ids, *junction_ids),
            (
                (location, reference)
                for index, edge in enumerate(self.edges)
                for location, reference in (
                    (("edges", index, "source"), edge.source),
                    (("edges", index, "target"), edge.target),
                )
            ),
            "Architecture node",
        )
        parents = {item.id: item.parent_id for item in self.groups}
        for group_index, group_id in enumerate(group_ids):
            visited: set[str] = set()
            current = group_id
            while current:
                if current in visited:
                    raise contract_validation_error(
                        type(self).__name__,
                        (
                            ModwireContractViolation(
                                ("groups", group_index, "parent_id"),
                                "cyclic_reference",
                                "Architecture group hierarchy contains a cycle",
                                self.groups[group_index].parent_id,
                            ),
                        ),
                    )
                visited.add(current)
                current = parents.get(current)
        service_groups = {item.id: item.group_id for item in self.services}
        for edge_index, edge in enumerate(self.edges):
            if edge.source_group_edge and not service_groups.get(edge.source):
                raise contract_validation_error(
                    type(self).__name__,
                    (
                        ModwireContractViolation(
                            ("edges", edge_index, "source_group_edge"),
                            "invalid_configuration",
                            "Architecture source group edges require a grouped service",
                            edge.source_group_edge,
                        ),
                    ),
                )
            if edge.target_group_edge and not service_groups.get(edge.target):
                raise contract_validation_error(
                    type(self).__name__,
                    (
                        ModwireContractViolation(
                            ("edges", edge_index, "target_group_edge"),
                            "invalid_configuration",
                            "Architecture target group edges require a grouped service",
                            edge.target_group_edge,
                        ),
                    ),
                )
        return self
