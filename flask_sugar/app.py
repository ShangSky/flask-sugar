import typing as t

from flask import Flask

from flask_sugar.view import View


class Sugar(Flask):
    def add_url_rule(
            self,
            rule: str,
            endpoint: t.Optional[str] = None,
            view_func: t.Optional[t.Callable] = None,
            provide_automatic_options: t.Optional[bool] = None,
            **options: t.Any,
    ) -> None:
        view = View(rule, view_func)
        super(Sugar, self).add_url_rule(rule, endpoint, view.as_view(), provide_automatic_options, **options)
