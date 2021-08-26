# 请求头参数

您可以像定义 `Query`、`Path`和`Cookie`参数一样定义 Header 参数.

## 导入`Header`

首先，导入`Header`:

```python hl_lines="3"
from typing import Optional

from flask_sugar import Sugar, Header

app = Sugar(__name__)


@app.get("/")
def index(user_agent: Optional[str] = Header(None)):
    return {"user_agent": user_agent}
```

## 声明`Header`参数

然后使用与`Path`、`Query`和`Cookie`相同的结构声明头参数.

第一个值是默认值，您可以传递所有额外的验证或注释参数:

```python hl_lines="9"
from typing import Optional

from flask_sugar import Sugar, Header

app = Sugar(__name__)


@app.get("/")
def index(user_agent: Optional[str] = Header(None)):
    return {"user_agent": user_agent}
```

!!! note "技术细节"
    `Header` 是 `Path` 和 `Query` 的“姐妹”类。 它们继承自 `Param` 类。

    但请记住，当你从 `flask_sugar` 中导入 `Query`、`Path`、`Header` 等时，这些实际上是返回特殊类的函数.

!!! info
    要声明header，您需要使用`Header`，否则参数将被解释为查询参数.

## 自动转换

`Header`在`Path`、`Query`和`Cookie`提供的基础上有一些额外的功能.

大多数标准标题由"连字符"字符分隔，也称为"减号"(-).

但是像`user-agent`这样的变量在 Python 中是无效的。

因此，默认情况下，`Header` 会将参数名称字符从下划线 (`_`) 转换为连字符 (`-`) 以提取和记录请求头。

此外，HTTP 标头不区分大小写，因此您可以使用标准 Python 样式（也称为“蛇形命名法”）声明它们。

因此，您可以像在 Python 代码中通常使用的那样使用 `user_agent`，而不需要将首字母大写为 `User_Agent` 或类似的东西。

## header列表

可能会收到具有多个值的同一个header。

您可以使用类型声明中的列表来定义这些情况。

您将把 header 中的值分割为 Python的`list`.

例如, 声明一个具有多个值的header `X-Token`, 你可以这样写:

```python hl_lines="9"
from flask_sugar import Sugar, Header

app = Sugar(__name__)


@app.get("/")
def index(x_token: List[str] = Header(None)):
    return {"X-Token values": x_token}
```

你将发送一个这样的header与视图函数通信:

```
X-Token: foo,bar
```

响应将类似于:

```JSON
{
    "X-Token values": [
        "bar",
        "foo"
    ]
}
```

## 回顾

使用`Header`声明header，使用与`Query`和`Path`相同的通用模式.

并且不要担心变量中的下划线，**FLask Sugar** 将负责转换它们。
