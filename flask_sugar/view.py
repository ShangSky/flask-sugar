import typing as t
from functools import update_wrapper


class View:
    """wrap view_func"""

    def __init__(self, view_func: t.Optional[t.Callable] = None) -> None:
        self.view_func = view_func
        update_wrapper(self, view_func)  # type:ignore

    def __call__(self, *args, **kwargs) -> t.Any:
        if self.view_func is None:
            return self.view_func
        return self.view_func(*args, **kwargs)
