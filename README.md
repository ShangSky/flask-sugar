# Flask Sugar

- [简体中文](README_zh.md)

Flask Sugar is a web framework for building APIs with Flask, Pydantic and Python 3.6+ type hints.

check parameters and generate API documents automatically

Documentation: <https://shangsky.github.io/flask-sugar>

Source Code: <https://github.com/shangsky/flask-sugar>


## Requirements

- Python 3.6+
- Flask 2.0+

## Installation

```shell
$ pip install flask-sugar
```

## A Simple Example

```python
# save this as main.py
from typing import Any

from flask_sugar import Sugar
from typing_extensions import TypedDict

app = Sugar(__name__)


class Resp(TypedDict):
    code: int
    msg: str
    data: Any


@app.get("/")
def index() -> Resp:
    """index page"""
    return {"code": 0, "msg": "success", "data": {}}
```

```shell
$ export FLASK_APP=main:app
$ flask run --reload
  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Now visit the API documentation with Swagger UI at http://localhost:5000/doc:

![](https://github.com/ShangSky/flask-sugar/raw/main/docs/img/swagger-ui.png)

visit the API documentation with Redoc at http://localhost:5000/redoc:

![](https://github.com/ShangSky/flask-sugar/blob/main/docs/img/redoc.png)

## License

This project is licensed under the terms of the MIT license.