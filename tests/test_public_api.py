import modwire_mermaid


def test_root_api_is_intentionally_small():
    assert modwire_mermaid.__all__ == [
        "ModwireDiagramError",
        "ModwireMermaid",
        "ModwireMermaidFactory",
        "__version__",
    ]


def test_feature_packages_are_not_barrels():
    import modwire_mermaid.timeline

    assert not hasattr(modwire_mermaid.timeline, "ModwireTimeline")
