import pytest
from pydantic import ValidationError

from modwire_mermaid.graph import (
    ModwireFlowchart,
    ModwireFlowchartEdge,
    ModwireFlowchartLinkStyle,
    ModwireFlowchartNode,
    ModwireFlowchartStyleProperty,
)


def test_unknown_references_report_stable_code_and_nested_location():
    with pytest.raises(ValidationError) as captured:
        ModwireFlowchart(
            nodes=(ModwireFlowchartNode(id="known", label="Known"),),
            edges=(ModwireFlowchartEdge(source="missing", target="known", minimum_length=1),),
        )

    error = captured.value.errors()[0]
    assert error["type"] == "unknown_reference"
    assert error["loc"] == ("edges", 0, "source")
    assert error["ctx"] == {"label": "Flowchart edge", "reference": "missing"}


def test_link_indexes_report_stable_code_and_nested_location():
    with pytest.raises(ValidationError) as captured:
        ModwireFlowchart(
            nodes=(ModwireFlowchartNode(id="known", label="Known"),),
            link_styles=(
                ModwireFlowchartLinkStyle(
                    edge_indexes=(3,), properties=(ModwireFlowchartStyleProperty(name="stroke", value="red"),)
                ),
            ),
        )

    error = captured.value.errors()[0]
    assert error["type"] == "index_out_of_range"
    assert error["loc"] == ("link_styles", 0, "edge_indexes", 0)


def test_style_and_configuration_errors_remain_field_local():
    with pytest.raises(ValidationError) as style_error:
        ModwireFlowchartStyleProperty(name="stroke", value="red; injected")
    assert style_error.value.errors()[0]["loc"] == ("value",)

    with pytest.raises(ValidationError) as configuration_error:
        ModwireFlowchart(
            nodes=(ModwireFlowchartNode(id="known", label="Known"),),
            link_styles=(
                ModwireFlowchartLinkStyle(
                    use_default=True,
                    edge_indexes=(0,),
                    properties=(ModwireFlowchartStyleProperty(name="stroke", value="red"),),
                ),
            ),
        )
    error = configuration_error.value.errors()[0]
    assert error["type"] == "invalid_configuration"
    assert error["loc"] == ("link_styles", 0, "edge_indexes")
