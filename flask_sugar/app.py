import typing as t
from functools import wraps

from flask import Flask


def view_func_decorator(view_func: t.Optional[t.Callable] = None) -> t.Optional[t.Callable]:
    """包装view_func"""
    if not view_func:
        return view_func

    @wraps(view_func)
    def new_view_func(*args: t.Any, **kwargs: t.Any) -> t.Any:
        return view_func(*args, **kwargs)

    return new_view_func


class Sugar(Flask):
    def add_url_rule(
            self,
            rule: str,
            endpoint: t.Optional[str] = None,
            view_func: t.Optional[t.Callable] = None,
            provide_automatic_options: t.Optional[bool] = None,
            **options: t.Any,
    ) -> None:
        view_func = view_func_decorator(view_func)
        super(Sugar, self).add_url_rule(rule, endpoint, view_func, provide_automatic_options, **options)
