from ..style_rendering import MermaidStyleRendering
from ..syntax import MermaidSyntax
from .diagram import (
    ModwireClassAttribute,
    ModwireClassMember,
    ModwireClassParameter,
    ModwireClassRelationship,
    ModwireClassStyleProperty,
)


class ModwireClassRendering:
    @classmethod
    def member(cls, member: ModwireClassMember) -> str:
        if isinstance(member, ModwireClassAttribute):
            suffix = "$" if member.is_static else ""
            return f"{member.visibility.value}{MermaidSyntax.raw(member.type)} {MermaidSyntax.raw(member.name)}{suffix}"
        parameters = ", ".join(cls.parameter(parameter) for parameter in member.parameters)
        classifiers = "".join(value.value for value in member.classifiers)
        return (
            f"{member.visibility.value}{MermaidSyntax.raw(member.name)}({parameters}) "
            f"{MermaidSyntax.raw(member.return_type)}{classifiers}"
        )

    @staticmethod
    def parameter(parameter: ModwireClassParameter) -> str:
        return f"{MermaidSyntax.raw(parameter.name)}: {MermaidSyntax.raw(parameter.type)}"

    @staticmethod
    def relationship_arrow(relationship: ModwireClassRelationship) -> str:
        return f"{relationship.source_end.value}{relationship.line.value}{relationship.target_end.value}"

    @staticmethod
    def style_property(value: ModwireClassStyleProperty) -> str:
        return MermaidStyleRendering.property(value.name, value.value)
