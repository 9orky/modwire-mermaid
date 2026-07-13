from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import ClassVar, Self, cast

from jinja2 import Environment, PackageLoader, StrictUndefined

from .contracts import ModwireBaseDiagram
from .syntax import MermaidSyntax


class DiagramTemplate[DiagramT: ModwireBaseDiagram](ABC):
    @abstractmethod
    def render(self, diagram: DiagramT) -> str:
        raise NotImplementedError


class JinjaDiagramTemplate[DiagramT: ModwireBaseDiagram](DiagramTemplate[DiagramT]):
    package: str
    name: str
    filters: ClassVar[Mapping[str, Callable[..., object]]] = MappingProxyType({})

    def __init__(self, environment: Environment, name: str):
        self._template = environment.get_template(name)

    @classmethod
    def standard(cls) -> Self:
        environment = Environment(
            loader=PackageLoader(cls.package, "."),
            undefined=StrictUndefined,
            autoescape=False,
            keep_trailing_newline=True,
        )
        environment.filters["mermaid_quote"] = MermaidSyntax.quote
        environment.filters["mermaid_label"] = cls._label
        environment.filters.update(cast(dict[str, Callable[..., object]], cls.filters))
        return cls(environment, cls.name)

    def render(self, diagram: DiagramT) -> str:
        return self._template.render(diagram=diagram).rstrip() + "\n"

    @staticmethod
    def _label(value: object) -> str:
        return MermaidSyntax.quote(str(value))[1:-1]
