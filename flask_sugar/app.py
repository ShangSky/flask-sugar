from typing import Optional, Callable, Any

from flask import Flask

from flask_sugar.blueprint import Blueprint
from flask_sugar.openapi import openapi_json_view, swagger, redoc
from flask_sugar.view import View


class Sugar(Flask):

    def add_url_rule(
            self,
            rule: str,
            endpoint: Optional[str] = None,
            view_func: Optional[Callable] = None,
            provide_automatic_options: Optional[bool] = None,
            doc_enable: bool = True,
            **options: Any,
    ) -> None:
        view = View(view_func, doc_enable)
        super().add_url_rule(rule, endpoint, view, provide_automatic_options, **options)

    def init_doc(self):
        openapi_url_prefix: str = self.config.get("SUGAR_OPENAPI_URL_PREFIX")
        openapi_json_url: str = self.config.get("SUGAR_OPENAPI_JSON_URL", "/openapi.json")
        swagger_url: str = self.config.get("SUGAR_SWAGGER_URL", "/doc")
        redoc_url: str = self.config.get("SUGAR_REDOC_URL", "/redoc")
        openapi_bp = Blueprint("openapi", __name__, url_prefix=openapi_url_prefix)
        if openapi_json_url:
            openapi_bp.add_url_rule(openapi_json_url, view_func=openapi_json_view, doc_enable=False)

        if swagger_url:
            openapi_bp.add_url_rule(swagger_url, view_func=swagger, doc_enable=False)

        if redoc_url:
            openapi_bp.add_url_rule(redoc_url, view_func=redoc, doc_enable=False)

        self.register_blueprint(openapi_bp)
