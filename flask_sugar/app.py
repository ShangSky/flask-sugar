import typing as t

from flask import Flask, Blueprint, render_template

from flask_sugar.view import View
from flask_sugar.openapi import get_openapi_json


class Sugar(Flask):
    def add_url_rule(
        self,
        rule: str,
        endpoint: t.Optional[str] = None,
        view_func: t.Optional[t.Callable] = None,
        provide_automatic_options: t.Optional[bool] = None,
        **options: t.Any,
    ) -> None:
        view = View(view_func)
        super().add_url_rule(rule, endpoint, view, provide_automatic_options, **options)

    def init_doc(self):
        doc_conf = self.config.get("FLASK_SUGAR_CONF") or {}
        openapi_json_url: str = doc_conf.get("openapi_json_url", "/openapi.json")
        swagger_url: str = doc_conf.get("swagger_url", "/doc")
        redoc_url: str = doc_conf.get("redoc_url", "/redoc")
        openapi_version: str = doc_conf.get("openapi_version", "3.0.2")
        title: str = doc_conf.get("title", "FlaskSugar")
        version: str = doc_conf.get("version", "0.1.0")
        description: t.Optional[str] = doc_conf.get("description", "")
        terms_service: t.Optional[str] = doc_conf.get("terms_service")
        contact: t.Optional[t.Dict[str, str]] = doc_conf.get("contact")
        license_: t.Optional[t.Dict[str, str]] = doc_conf.get("license_")
        servers: t.Optional[t.List[t.Dict[str, t.Union[str, t.Any]]]] = doc_conf.get(
            "servers"
        )
        swagger_js_url: str = doc_conf.get(
            "swagger_js_url",
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js",
        )
        swagger_css_url: str = doc_conf.get(
            "swagger_css_url",
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css",
        )
        redoc_js_url: str = doc_conf.get(
            "redoc_js_url",
            "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        )
        bp = Blueprint("flask_sugar", __name__, template_folder="templates")

        if openapi_json_url:

            @bp.get(openapi_json_url)
            def openapi_json_view() -> dict:
                return get_openapi_json(
                    openapi_version=openapi_version,
                    title=title,
                    version=version,
                    description=description,
                    terms_service=terms_service,
                    contact=contact,
                    license_=license_,
                    servers=servers,
                )

        if swagger_url:

            @bp.get(swagger_url)
            def swagger():
                return render_template(
                    "flask_sugar/swagger.html",
                    openapi_json_url=openapi_json_url,
                    title=title + " Swagger",
                    swagger_js_url=swagger_js_url,
                    swagger_css_url=swagger_css_url,
                )

        if redoc_url:

            @bp.get(redoc_url)
            def redoc():
                return render_template(
                    "flask_sugar/redoc.html",
                    openapi_json_url=openapi_json_url,
                    title=title + " Redoc",
                    redoc_js_url=redoc_js_url,
                )

        self.register_blueprint(bp)
