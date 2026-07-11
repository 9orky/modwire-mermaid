# Timeline diagrams

```python
from modwire_mermaid.timeline.diagram import ModwireTimeline
```

`ModwireTimeline` supports titles, ordered sections, periods with multiple events, LR and TD direction,
and the `disableMulticolor` timeline option.

For progressive construction, `ModwireTimelineBuilder` keeps intermediate state immutable and produces
the same validated contract:

```python
from modwire_mermaid.timeline.diagram import ModwireTimelineBuilder

diagram = (
    ModwireTimelineBuilder.create("Release history")
    .section("2026")
    .period("Q1", "Private beta")
    .period("Q2", "Public release", "Documentation")
    .build()
)
```
