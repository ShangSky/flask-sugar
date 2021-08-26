# 错误处理

如果需要更改验证错误的默认输出，可以覆盖RequestValidationError异常处理程序：

```python
from flask_sugar import Sugar, RequestValidationError

app = Sugar(__name__)


@app.errorhandler(RequestValidationError)
def error_handle(e: RequestValidationError):
    return {"detail": e.errors}
```