# Form Data

When you need to receive form fields instead of JSON, you can use `Form`.

## Import `Form`

Import `Form` from `flask_sugar`:

```Python hl_lines="1"
from flask_sugar import Sugar, Form
from pydantic import BaseModel

app = Sugar(__name__)


class LoginInfo(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(login_info: LoginInfo = Form(...)):
    return {"username": login_info.username}
```

## Define `Form` parameters

```Python hl_lines="13"
from flask_sugar import Sugar, Form
from pydantic import BaseModel

app = Sugar(__name__)


class LoginInfo(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(login_info: LoginInfo = Form(...)):
    return {"username": login_info.username}
```

For example, in one of the ways the OAuth2 specification can be used (called "password flow") it is required to send a `username` and `password` as form fields.

The <abbr title="specification">spec</abbr> requires the fields to be exactly named `username` and `password`, and to be sent as form fields, not JSON.

With `Form` you can declare the same metadata and validation as with `Body`

!!! info
    `Form` is a class that inherits directly from `Body`.

!!! tip
    To declare form bodies, you need to use `Form` explicitly, because without it the parameters would be interpreted as query parameters or body (JSON) parameters.

## About "Form Fields"

The way HTML forms (`<form></form>`) sends the data to the server normally uses a "special" encoding for that data, it's different from JSON.

**Flask Sugar** will make sure to read that data from the right place instead of JSON.

!!! note "Technical Details"
    Data from forms is normally encoded using the "media type" `application/x-www-form-urlencoded`.

    But when the form includes files, it is encoded as `multipart/form-data`. You'll read about handling files in the next chapter.
    
    If you want to read more about these encodings and form fields, head to the <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST" class="external-link" target="_blank"><abbr title="Mozilla Developer Network">MDN</abbr> web docs for <code>POST</code></a>.

!!! warning
    You can declare multiple `Form` parameters in a *path operation*, but you can't also declare `Body` fields that you expect to receive as JSON, as the request will have the body encoded using `application/x-www-form-urlencoded` instead of `application/json`.

    This is not a limitation of **Flask Sugar**, it's part of the HTTP protocol.

## Recap

Use `Form` to declare form data input parameters.
