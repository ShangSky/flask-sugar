# cookie参数

您可以像定义 `Query` 和 `Path` 参数一样定义 Cookie 参数.

## 导入 `Cookie`

首先，导入`Cookie`:

```python hl_lines="3"
from typing import Optional

from flask_sugar import Sugar, Cookie

app = Sugar(__name__)


@app.get("/")
def index(cookie_value: Optional[str] = Cookie(None)):
    return {"cookie_value": cookie_value}
```

## 声明 `Cookie` 参数

然后使用与 `Path` 和 `Query` 相同的结构声明 cookie 参数.

第一个值是默认值，您可以传递所有额外的验证或注释参数:

```python hl_lines="9"
from typing import Optional

from flask_sugar import Sugar, Cookie

app = Sugar(__name__)


@app.get("/")
def index(cookie_value: Optional[str] = Cookie(None)):
    return {"cookie_value": cookie_value}
```

!!! note "技术细节"
    `Cookie` 是 `Path` 和 `Query` 的“姐妹”类。 它们继承自 `Param` 类.

    但请记住，当你从 `flask_sugar` 中导入 `Query`、`Path`、`Cookie` 等时，这些实际上是返回特殊类的函数.

!!! info
    要声明cookie，您需要使用`Cookie`，否则参数将被解释为查询参数.

## cookie 列表 

可能会收到具有多个值的同一个cookie.

您可以使用类型声明中的列表来定义这些情况.

您将把 cookie 中的值分割为 Python的`list`.

例如, 声明一个具有多个值的cookie `values`, 你可以这样写:

```python hl_lines="9"
from flask_sugar import Sugar, Cookie

app = Sugar(__name__)


@app.get("/")
def index(values: List[str] = Cookie(None)):
    return {"values": values}
```

你将发送一个这样的cookie与视图函数通信:

```
values: foo,bar
```

响应将类似于：

```JSON
{
    "values": [
        "bar",
        "foo"
    ]
}
```

## 回顾

使用`Cookie`声明cookie，使用与`Query`和`Path`相同的通用模式.
