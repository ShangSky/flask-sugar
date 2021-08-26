# Cookie Parameters

You can define Cookie parameters the same way you define `Query` and `Path` parameters.

## Import `Cookie`

First import `Cookie`:

```python hl_lines="3"
from typing import Optional

from flask_sugar import Sugar, Cookie

app = Sugar(__name__)


@app.get("/")
def index(cookie_value: Optional[str] = Cookie(None)):
    return {"cookie_value": cookie_value}
```

## Declare `Cookie` parameters

Then declare the cookie parameters using the same structure as with `Path` and `Query`.

The first value is the default value, you can pass all the extra validation or annotation parameters:

```python hl_lines="9"
from typing import Optional

from flask_sugar import Sugar, Cookie

app = Sugar(__name__)


@app.get("/")
def index(cookie_value: Optional[str] = Cookie(None)):
    return {"cookie_value": cookie_value}
```

!!! note "Technical Details"
    `Cookie` is a "sister" class of `Path` and `Query`. It also inherits from the same common `Param` class.

    But remember that when you import `Query`, `Path`, `Cookie` and others from `flask_sugar`, those are actually functions that return special classes.

!!! info
    To declare cookies, you need to use `Cookie`, because otherwise the parameters would be interpreted as query parameters.

## List cookies

It is possible to receive a cookie with multiple values.

You can define those cases using a list in the type declaration.

You will split the value in the cookie into a Python `list`.

For example, to declare a cookie values with multiple values, you can write:

```python hl_lines="9"
from flask_sugar import Sugar, Cookie

app = Sugar(__name__)


@app.get("/")
def index(values: List[str] = Cookie(None)):
    return {"values": values}
```

If you communicate with that *path operation* sending a cookie like:

```
values: foo,bar
```

The response would be like:

```JSON
{
    "values": [
        "bar",
        "foo"
    ]
}
```

## Recap

Declare cookies with `Cookie`, using the same common pattern as `Query` and `Path`.
