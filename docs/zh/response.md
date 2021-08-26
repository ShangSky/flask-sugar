# 响应

你可以在任意的*路径操作*中使用 `response_model` 参数来声明用于响应的模型：

* `@app.get()`
* `@app.post()`
* `@app.put()`
* `@app.delete()`

或者在返回值的typehint中声明model/TypedDict。

## 在装饰器参数中使用`response_model`

```python hl_lines="17 19 22 24"
from typing import List, Optional

from flask_sugar import Sugar
from pydantic import BaseModel

app = Sugar(__name__)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    tags: List[str] = []


@app.post("/item1/", response_model=Item)
def create_item1(item: Item):
    return item


@app.post("/item2/", response_model=Item)
def create_item2(item: Item):
    return item.dict()
```

![FLask Sugar Response](../img/response.png)

!!! note
    注意，`response_model`是「装饰器」方法（`get`，`post` 等）的一个参数。不像之前的所有参数和请求体，它不属于*路径操作函数*。

*路径操作*的返回值可以是一个字典或者模型。

它接收的类型与你将为 Pydantic 模型属性所声明的类型相同，因此它可以是一个 Pydantic 模型。

Flask Sugar 将使用此 `response_model` 来：

* 将输出数据转换为其声明的类型。
* 校验数据。
* 在 OpenAPI 的*路径操作*中为响应添加一个 JSON Schema。
* 并在自动生成文档系统中使用。

但最重要的是：

* 会将输出数据限制在该模型定义内。下面我们会看到这一点有多重要。

!!! note "技术细节"
    响应模型在参数中被声明，而不是作为函数返回类型的注解，这是因为路径函数可能不会真正返回该响应模型，而是返回一个 `dict`、数据库对象或其他模型，然后再使用 `response_model` 来执行字段约束和序列化。

## 在类型注解中使用模型

```python hl_lines="17"
from typing import List, Optional

from flask_sugar import Sugar
from pydantic import BaseModel

app = Sugar(__name__)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    tags: List[str] = []


@app.post("/items/")
def create_item(item: Item) -> Item:
    return item
```

它和在装饰器参数中使用效果一样

## 在类型注解中使用`TypedDict`

```python hl_lines="16"
from typing import List
from typing_extensions import TypedDict

from flask_sugar import Sugar

app = Sugar(__name__)


class UserInfo(TypedDict):
    name: str
    age: int
    tags: List[str]


@app.get("/")
def index() -> UserInfo:
    return {"name": "rockman", "age": 25, "tags": ["a", "b"]}
```

!!! note
    你不要**路径操作**的参数和**装饰器**中使用TypedDict.  
    它只在返回值的类型注解生效。

`TypedDict`在代码静态检查和实际运行时检查**路径操作**的返回值

## 响应模型编码参数

你的响应模型可以具有默认值，例如：

```Python hl_lines="11  13-14"
from typing import List, Optional

from flask_sugar import Sugar
from pydantic import BaseModel

app = Sugar(__name__)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: float = 10.5
    tags: List[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get("/items/<item_id>", response_model=Item, response_model_exclude_unset=True)
def read_item(item_id: str):
    return items[item_id]
```

* `description: Optional[str] = None` 具有默认值 `None`。
* `tax: float = 10.5` 具有默认值 `10.5`.
* `tags: List[str] = []` 具有一个空列表作为默认值： `[]`.

但如果它们并没有存储实际的值，你可能想从结果中忽略它们的默认值。

举个例子，当你在 NoSQL 数据库中保存了具有许多可选属性的模型，但你又不想发送充满默认值的很长的 JSON 响应。

### 使用 `response_model_exclude_unset` 参数

你可以设置*路径操作装饰器*的 `response_model_exclude_unset=True` 参数：

```Python hl_lines="24"
from typing import List, Optional

from flask_sugar import Sugar
from pydantic import BaseModel

app = Sugar(__name__)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: float = 10.5
    tags: List[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get("/items/<item_id>", response_model=Item, response_model_exclude_unset=True)
def read_item(item_id: str):
    return items[item_id]
```

然后响应中将不会包含那些默认值，而是仅有实际设置的值。

因此，如果你向*路径操作*发送 ID 为 `foo` 的商品的请求，则响应（不包括默认值）将为：

```JSON
{
    "name": "Foo",
    "price": 50.2
}
```

!!! info
    Flask Sugar 通过 Pydantic 模型的 `.dict()` 配合 <a href="https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeldict" class="external-link" target="_blank">该方法的 `exclude_unset` 参数</a> 来实现此功能。

!!! info
    你还可以使用：

    * `response_model_exclude_defaults=True`
    * `response_model_exclude_none=True`

    参考 <a href="https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeldict" class="external-link" target="_blank">Pydantic 文档</a> 中对 `exclude_defaults` 和 `exclude_none` 的描述。

#### 默认值字段有实际值的数据

但是，如果你的数据在具有默认值的模型字段中有实际的值，例如 ID 为 `bar` 的项：

```Python hl_lines="3  5"
{
    "name": "Bar",
    "description": "The bartenders",
    "price": 62,
    "tax": 20.2
}
```

这些值将包含在响应中。

#### 具有与默认值相同值的数据

如果数据具有与默认值相同的值，例如 ID 为 `baz` 的项：

```Python hl_lines="3  5-6"
{
    "name": "Baz",
    "description": None,
    "price": 50.2,
    "tax": 10.5,
    "tags": []
}
```

即使 `description`、`tax` 和 `tags` 具有与默认值相同的值，Flask Sugar 足够聪明 (实际上是 Pydantic 足够聪明) 去认识到这一点，它们的值被显式地所设定（而不是取自默认值）。

因此，它们将包含在 JSON 响应中。

!!! tip
    请注意默认值可以是任何值，而不仅是`None`。

    它们可以是一个列表（`[]`），一个值为 `10.5`的 `float`，等等。

### `response_model_include` 和 `response_model_exclude`

你还可以使用*路径操作装饰器*的 `response_model_include` 和 `response_model_exclude` 参数。

它们接收一个由属性名称 `str` 组成的 `set` 来包含（忽略其他的）或者排除（包含其他的）这些属性。

如果你只有一个 Pydantic 模型，并且想要从输出中移除一些数据，则可以使用这种快捷方法。

!!! tip
    但是依然建议你使用上面提到的主意，使用多个类而不是这些参数。

    这是因为即使使用 `response_model_include` 或 `response_model_exclude` 来省略某些属性，在应用程序的 OpenAPI 定义（和文档）中生成的 JSON Schema 仍将是完整的模型。

    这也适用于作用类似的 `response_model_by_alias`。

```Python hl_lines="31  37"
from typing import Optional

from flask_sugar import Sugar
from pydantic import BaseModel

app = Sugar(__name__)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: float = 10.5


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The Bar fighters", "price": 62, "tax": 20.2},
    "baz": {
        "name": "Baz",
        "description": "There goes my baz",
        "price": 50.2,
        "tax": 10.5,
    },
}


@app.get(
    "/items/<item_id>/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
def read_item_name(item_id: str):
    return items[item_id]


@app.get("/items/<item_id>/public", response_model=Item, response_model_exclude={"tax"})
def read_item_public_data(item_id: str):
    return items[item_id]
```

!!! tip
    `{"name", "description"}` 语法创建一个具有这两个值的 `set`。

    等同于 `set(["name", "description"])`。

## 小结

使用*路径操作装饰器*的 `response_model` 参数来定义响应模型，特别是确保私有数据被过滤掉。

使用 `response_model_exclude_unset` 来仅返回显式设定的值。

