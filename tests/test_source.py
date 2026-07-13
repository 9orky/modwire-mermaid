import pytest

from modwire_mermaid.source import MermaidWriter


def test_mermaid_writer_owns_indentation_and_final_newline():
    source = MermaidWriter(indentation="  ")

    source.line("diagram", depth=0)
    source.line("section", depth=1)
    source.lines(("first", "second"), depth=2)

    assert source.render() == "diagram\n  section\n    first\n    second\n"


def test_mermaid_writer_rejects_invalid_lines_and_depths():
    source = MermaidWriter(indentation="  ")

    with pytest.raises(ValueError, match="line breaks"):
        source.line("first\nsecond", depth=0)
    with pytest.raises(ValueError, match="negative"):
        source.line("line", depth=-1)


def test_mermaid_writer_requires_explicit_indentation():
    with pytest.raises(ValueError, match="indentation"):
        MermaidWriter(indentation="")


def test_mermaid_writer_normalizes_line_endings_and_final_newline():
    source = MermaidWriter()
    source.block("first\r\nsecond\rthird\n\n")

    assert source.render() == "first\nsecond\nthird\n"
