# Flask Sugar
Flask Sugar is a web framework for building APIs with Flask, Pydantic and Python 3.6+ type hints.

check parameters and generate API documents automatically

Documentation: <https://shangsky.github.io/flask-sugar> or <https://flask-sugar.vercel.app/>

Source Code: <https://github.com/shangsky/flask-sugar>


## Requirements

- Python 3.6+
- Flask 2.0+

## Installation

```shell
$ pip install flask-sugar
```

## Example

```python
# save this as app.py
from flask_sugar import Sugar, Header
from pydantic import BaseModel

app = Sugar(__name__)


class Item(BaseModel):
    name: str
    size: int


class Resp(BaseModel):
    a: int
    b: str
    c: str
    item: Item


@app.post("/item/<a>")
def demo(
    a: int,  # path param
    item: Item,  # json body param
    b: str = "default_query_param_b",  # query param
    c: str = Header("default_header_param_b"),  # request header param
) -> Resp:
    """demo page"""
    return Resp(a=a, b=b, c=c, item=item)
```

```shell
$ flask run --reload
  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Now visit the API documentation with Swagger UI at http://localhost:5000/doc:

![](img/swagger-ui.png)

visit the API documentation with Redoc at http://localhost:5000/redoc:

![](img/redoc.png)

## License

This project is licensed under the terms of the MIT license.