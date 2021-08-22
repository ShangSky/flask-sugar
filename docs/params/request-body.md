# Request Body

When you need to send data from a client (let's say, a browser) to your API, you send it as a **request body**.

A **request** body is data sent by the client to your API. A **response** body is the data your API sends to the client.

Your API almost always has to send a **response** body. But clients don't necessarily need to send **request** bodies all the time.

To declare a **request** body, you use <a href="https://pydantic-docs.helpmanual.io/" class="external-link" target="_blank">Pydantic</a> models with all their power and benefits.


## Import Pydantic's `BaseModel`

First, you need to import `BaseModel` from `pydantic`:

```Python hl_lines="4"
from typing import Optional

from flask_sugar import Sugar
from pydantic import BaseModel

app = Sugar(__name__)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


@app.post("/items/")
def create(item: Item):
    return item
```

## Create your data model

Then you declare your data model as a class that inherits from `BaseModel`.

Use standard Python types for all the attributes:

```Python hl_lines="9-13"
from typing import Optional

from flask_sugar import Sugar
from pydantic import BaseModel

app = Sugar(__name__)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


@app.post("/items/")
def create(item: Item):
    return item
```

The same as when declaring query parameters, when a model attribute has a default value, it is not required. Otherwise, it is required. Use `None` to make it just optional.

For example, this model above declares a JSON "`object`" (or Python `dict`) like:

```JSON
{
    "name": "Foo",
    "description": "An optional description",
    "price": 45.2,
    "tax": 3.5
}
```

...as `description` and `tax` are optional (with a default value of `None`), this JSON "`object`" would also be valid:

```JSON
{
    "name": "Foo",
    "price": 45.2
}
```

## Declare it as a parameter

To add it to your *path operation*, declare it the same way you declared path and query parameters:

```Python hl_lines="17"
from typing import Optional

from flask_sugar import Sugar
from pydantic import BaseModel

app = Sugar(__name__)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


@app.post("/items/")
def create(item: Item):
    return item
```

...and declare its type as the model you created, `Item`.

## Results

With just that Python type declaration, **Flask Sugar** will:

* Read the body of the request as JSON.
* Convert the corresponding types (if needed).
* Validate the data.
    * If the data is invalid, it will return a nice and clear error, indicating exactly where and what was the incorrect data.
* Give you the received data in the parameter `item`.
    * As you declared it in the function to be of type `Item`, you will also have all the editor support (completion, etc) for all of the attributes and their types.
* Generate <a href="https://json-schema.org" class="external-link" target="_blank">JSON Schema</a> definitions for your model, you can also use them anywhere else you like if it makes sense for your project.
* Those schemas will be part of the generated OpenAPI schema, and used by the automatic documentation <abbr title="User Interfaces">UIs</abbr>.

## Automatic docs

The JSON Schemas of your models will be part of your OpenAPI generated schema, and will be shown in the interactive API docs:

<img src="/img/body-image01.png">

And will be also used in the API docs inside each *path operation* that needs them:

<img src="/img/body-image02.png">

## Use the model

Inside of the function, you can access all the attributes of the model object directly:

```Python hl_lines="20"
from typing import Optional

from flask_sugar import Sugar
from pydantic import BaseModel

app = Sugar(__name__)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


@app.post("/items/")
def create(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict
```

## Request body + path parameters

You can declare path parameters and request body at the same time.

**Flask Sugar** will recognize that the function parameters that match path parameters should be **taken from the path**, and that function parameters that are declared to be Pydantic models should be **taken from the request body**.

```Python hl_lines="16-17"
from typing import Optional

from flask_sugar import Sugar
from pydantic import BaseModel

app = Sugar(__name__)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


@app.put("/items/<item_id>")
def create(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}
```

## Request body + path + query parameters

You can also declare **body**, **path** and **query** parameters, all at the same time.

**Flask Sugar** will recognize each of them and take the data from the correct place.

```Python hl_lines="17"
from typing import Optional

from flask_sugar import Sugar
from pydantic import BaseModel

app = Sugar(__name__)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


@app.post("/items/<item_id>")
def create(item_id: int, item: Item, q: Optional[str] = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result
```

The function parameters will be recognized as follows:

* If the parameter is also declared in the **path**, it will be used as a path parameter.
* If the parameter is of a **singular type** (like `int`, `float`, `str`, `bool`, etc) it will be interpreted as a **query** parameter.
* If the parameter is declared to be of the type of a **Pydantic model**, it will be interpreted as a request **body**.

!!! note
    Flask Sugar will know that the value of `q` is not required because of the default value `= None`.

    The `Optional` in `Optional[str]` is not used by Flask Sugar, but will allow your editor to give you better support and detect errors.
