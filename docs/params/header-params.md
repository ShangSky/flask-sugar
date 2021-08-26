# Header Parameters

You can define Header parameters the same way you define `Query`, `Path` and `Cookie` parameters.

## Import `Header`

First import `Header`:

```python hl_lines="3"
from typing import Optional

from flask_sugar import Sugar, Header

app = Sugar(__name__)


@app.get("/")
def index(user_agent: Optional[str] = Header(None)):
    return {"user_agent": user_agent}
```

## Declare `Header` parameters

Then declare the header parameters using the same structure as with `Path`, `Query` and `Cookie`.

The first value is the default value, you can pass all the extra validation or annotation parameters:

```python hl_lines="9"
from typing import Optional

from flask_sugar import Sugar, Header

app = Sugar(__name__)


@app.get("/")
def index(user_agent: Optional[str] = Header(None)):
    return {"user_agent": user_agent}
```

!!! note "Technical Details"
    `Header` is a "sister" class of `Path`, `Query` and `Cookie`. It also inherits from the same common `Param` class.

    But remember that when you import `Query`, `Path`, `Header`, and others from `flask_sugar`, those are actually functions that return special classes.

!!! info
    To declare headers, you need to use `Header`, because otherwise the parameters would be interpreted as query parameters.

## Automatic conversion

`Header` has a little extra functionality on top of what `Path`, `Query` and `Cookie` provide.

Most of the standard headers are separated by a "hyphen" character, also known as the "minus symbol" (`-`).

But a variable like `user-agent` is invalid in Python.

So, by default, `Header` will convert the parameter names characters from underscore (`_`) to hyphen (`-`) to extract and document the headers.

Also, HTTP headers are case-insensitive, so, you can declare them with standard Python style (also known as "snake_case").

So, you can use `user_agent` as you normally would in Python code, instead of needing to capitalize the first letters as `User_Agent` or something similar.

## List headers

It is possible to receive a header with multiple values.

You can define those cases using a list in the type declaration.

You will split the value in the header into a Python `list`.

For example, to declare a header values with multiple values, you can write:

```python hl_lines="9"
from flask_sugar import Sugar, Header

app = Sugar(__name__)


@app.get("/")
def index(x_token: List[str] = Header(None)):
    return {"X-Token values": x_token}
```

If you communicate with that *path operation* sending a HTTP headers like:

```
X-Token: foo,bar
```

The response would be like:

```JSON
{
    "X-Token values": [
        "bar",
        "foo"
    ]
}
```

## Recap

Declare headers with `Header`, using the same common pattern as `Query`, `Path` and `Cookie`.

And don't worry about underscores in your variables, **FLask Sugar** will take care of converting them.
