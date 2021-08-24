# Handling Errors

If you need to change default output for validation errors - override RequestValidationError exception handler:

```python
from flask_sugar import Sugar, RequestValidationError

app = Sugar(__name__)


@app.errorhandler(RequestValidationError)
def error_handle(e: RequestValidationError):
    return {"detail": e.errors}
```