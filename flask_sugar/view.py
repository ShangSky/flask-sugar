import typing as t
from functools import wraps


def view_func_decorator(view_func: t.Optional[t.Callable] = None) -> t.Optional[t.Callable]:
    """wrap view_func"""
    if not view_func:
        return view_func

    @wraps(view_func)
    def new_view_func(*args: t.Any, **kwargs: t.Any) -> t.Any:
        return view_func(*args, **kwargs)

    return new_view_func


class View:
    def __init__(self, rule: str, view_func: t.Optional[t.Callable] = None) -> None:
        self.rule = rule
        self.view_func = view_func

    def as_view(self) -> t.Optional[t.Callable]:
        return view_func_decorator(self.view_func)
