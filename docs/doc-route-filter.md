# DocRouteFilter

You can use doc_route_filter to filter or set route-related properties in the document

## example

Filter out routes starting with `/b`

```python
from flask_sugar import Sugar

app = Sugar(__name__, doc_route_filter=lambda view, rule: not rule.rule.startswith("/b"))


@app.get("/a/1")
def a1():
    return "a1"


@app.get("/b/1")
def b1():
    return "a2"
```

![](img/doc-route-filter.png)