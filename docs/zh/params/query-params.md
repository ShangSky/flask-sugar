# 查询参数

当您声明不属于路径参数的其他函数参数时，它们将自动解释为“查询”参数。

```python
nums = list(range(100))


@app.get("/nums")
def get_nums(limit: int = 10, offset: int = 0):
    return {"results": nums[offset: offset + limit]}
```

你可以访问这样的url去使用这个视图函数:

```
http://localhost:5000/nums?offset=0&limit=10
```
默认情况下，所有GET参数都是字符串，当您为函数参数添加类型注释时，它们将转换为该类型并根据该类型进行验证。

路径参数的好处也同样适用于查询参数:

- 编辑器友好
- 数据解析
- 数据校验
- 自动生成文档

注意: 当你没有给你的参数加类型注解时, 它们将会被视为`str`类型:

```python
@app.get("/nums")
def get_nums(limit, offset):
    # type(limit) == str
    # type(offset) == str
```

### 默认值

由于查询参数不是url路径的组成部分，它们是可选的并且可以具有默认值:

```python
@app.get("/nums")
def get_nums(limit: int = 10, offset: int = 0):
    return nums[offset: offset + limit]
```

在上面的例子中，我们设置了默认值 offset=0 和 limit=10.

所以, 访问网址:
```
http://localhost:5000/nums
```
访问下面地址效果相同:
```
http://localhost:5000/nums?offset=0&limit=10
```
如果你访问了例子的url:
```
http://localhost:5000/nums?offset=20
```

你函数中的参数值将是:

 - `offset=20`  (因为你在url中设置了offset)
 - `limit=10`  (因为它是默认值)

### 必须和可选参数

您可以使用与声明 Python 函数参数相同的方式声明必需或可选的 GET 参数:

```python
nums = list(range(100))


@app.get("/nums")
def get_nums(greater_than: int, offset: int = 10):
    results = [num for num in nums if num > greater_than]
    return {"results": results[offset: offset + 10]}
```

在这种情况下，Flask Sugar 将始终验证您在 GET 中传递的`greater_than`参数，并且`offset`参数是一个可选整数.

## 校验更多参数(使用pydantic)

```python
from flask_sugar import Sugar, Query

app = Sugar(__name__)


@app.get("/nums")
def get_nums(limit: Optional[int] = Query(default=10, le=25), offset: Optional[int] = Query(default=0)):
    return nums[offset: offset + limit]
```

在上面的例子中，我们设置了默认值 offset=0 和 limit=10,  limit的值必须小于或者等于25


### GET参数类型转换

我们来定义多个参数:

```python
from datetime import date


@app.get("/example")
def example(s: str = None, b: bool = None, d: date = None, i: int = None):
    return {"value": [s, b, d, i]}
```

类型为`str`的参数将会被原样传递.

类型为`bool`的参数, 像下面这样的:

```
http://localhost:5000/example?b=1
http://localhost:5000/example?b=True
http://localhost:5000/example?b=true
http://localhost:5000/example?b=on
http://localhost:5000/example?b=yes
```

或任何其他大小写变体（大写、大写的第一个字母等），您的函数将看到参数`b`的`bool`值为`True`，否则为`False`.

日期可以是日期字符串和整数(unix时间戳):

```
http://localhost:5000/example?d=1577836800  # same as 2020-01-01
http://localhost:5000/example?d=2020-01-01
```