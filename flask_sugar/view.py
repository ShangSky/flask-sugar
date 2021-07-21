import typing as t
from functools import update_wrapper


class View:
    """wrap view_func"""

    def __init__(
        self, view_func: t.Optional[t.Callable] = None, doc_enable: bool = True
    ) -> None:
        self.view_func = view_func
        update_wrapper(self, view_func)  # type:ignore
        self.doc_enable = doc_enable

    def __call__(self, *args, **kwargs) -> t.Any:
        if self.view_func is None:
            return self.view_func
        return self.view_func(*args, **kwargs)

    def __str__(self):
        return f"View(view_func={self.view_func}, doc_enable={self.doc_enable})"
