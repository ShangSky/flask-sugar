# Query Parameters

When you declare other function parameters that are not part of the path parameters, they are automatically interpreted as "query" parameters.

```python
nums = list(range(100))


@app.get("/nums")
def get_nums(limit: int = 10, offset: int = 0):
    return {"results": nums[offset: offset + limit]}
```

To query this operation, you use a URL like:

```
http://localhost:5000/nums?offset=0&limit=10
```
By default, all GET parameters are strings, and when you annotate your function arguments with types, they are converted to that type and validated against it.

The same benefits that apply to path parameters also apply to query parameters:

- Editor support (obviously)
- Data "parsing"
- Data validation
- Automatic documentation

Note: if you do not annotate your arguments, they will be treated as `str` types:

```python
@app.get("/nums")
def get_nums(limit, offset):
    # type(limit) == str
    # type(offset) == str
```

### Defaults

As query parameters are not a fixed part of a path, they are optional and can have default values:

```python
@app.get("/nums")
def get_nums(limit: int = 10, offset: int = 0):
    return nums[offset: offset + limit]
```

In the example above we set default values of `offset=0` and `limit=10`.

So, going to the URL:
```
http://localhost:5000/nums
```
would be the same as going to:
```
http://localhost:5000/nums?offset=0&limit=10
```
If you go to, for example:
```
http://localhost:5000/nums?offset=20
```

the parameter values in your function will be:

 - `offset=20`  (because you set it in the URL)
 - `limit=10`  (because that was the default value)

### Required and optional parameters

You can declare required or optional GET parameters in the same way as declaring Python function arguments:

```python
nums = list(range(100))


@app.get("/nums")
def get_nums(greater_than: int, offset: int = 10):
    results = [num for num in nums if num > greater_than]
    return {"results": results[offset: offset + 10]}
```

In this case, Flask Sugar will always validate that you pass the `greater_than` param in the GET, and the `offset` param is an optional integer.

## More validation by pydantic

```python
from flask_sugar import Sugar, Query

app = Sugar(__name__)


@app.get("/nums")
def get_nums(limit: Optional[int] = Query(default=10, le=25), offset: Optional[int] = Query(default=0)):
    return nums[offset: offset + limit]
```

In the example above we set default values of `offset=0` and `limit=10`, and Flask Sugar will always validate the `limit` must be less than or equal to 25. 

### GET parameters type conversion

Let's declare multiple type arguments:
```python
from datetime import date


@app.get("/example")
def example(s: str = None, b: bool = None, d: date = None, i: int = None):
    return {"value": [s, b, d, i]}
```
The `str` type is passed as is.

For the `bool` type, all the following:
```
http://localhost:5000/example?b=1
http://localhost:5000/example?b=True
http://localhost:5000/example?b=true
http://localhost:5000/example?b=on
http://localhost:5000/example?b=yes
```
or any other case variation (uppercase, first letter in uppercase, etc), your function will see the parameter `b` with a `bool` value of `True`, otherwise as `False`.

Date can be both date string and integer (unix timestamp):

```
http://localhost:5000/example?d=1577836800  # same as 2020-01-01
http://localhost:5000/example?d=2020-01-01
```