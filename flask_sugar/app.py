from typing import Optional, Callable, Any, Dict, List, Union

from flask import Flask

from flask_sugar.blueprint import Blueprint
from flask_sugar.openapi import openapi_json_view, swagger, redoc
from flask_sugar.view import View


class Sugar(Flask):
    def __init__(
        self,
        import_name: str,
        static_url_path: Optional[str] = None,
        static_folder: Optional[str] = "static",
        static_host: Optional[str] = None,
        host_matching: bool = False,
        subdomain_matching: bool = False,
        template_folder: Optional[str] = "templates",
        instance_path: Optional[str] = None,
        instance_relative_config: bool = False,
        root_path: Optional[str] = None,
        title: str = "FlaskSugar",
        doc_version: str = "0.1.0",
        description: Optional[str] = None,
        terms_service: Optional[str] = None,
        contact: Optional[Dict[str, str]] = None,
        license_: Optional[Dict[str, str]] = None,
        servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
        tags: Optional[List[Dict[str, Any]]] = None,
        openapi_url_prefix: Optional[str] = None,
        openapi_json_url: str = "/openapi.json",
        swagger_url: str = "/doc",
        redoc_url: str = "/redoc",
        swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js",
        swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css",
        redoc_js_url: str = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    ):
        super().__init__(
            import_name=import_name,
            static_url_path=static_url_path,
            static_folder=static_folder,
            static_host=static_host,
            host_matching=host_matching,
            subdomain_matching=subdomain_matching,
            template_folder=template_folder,
            instance_path=instance_path,
            instance_relative_config=instance_relative_config,
            root_path=root_path,
        )
        self.title = title
        self.doc_version = doc_version
        self.description = description
        self.terms_service = terms_service
        self.contact = contact
        self.license_ = license_
        self.servers = servers
        self.tags = tags
        self.openapi_url_prefix = openapi_url_prefix
        self.openapi_json_url = openapi_json_url
        self.swagger_url = swagger_url
        self.redoc_url = redoc_url
        self.openapi_version = "3.0.2"
        self.swagger_js_url = swagger_js_url
        self.swagger_css_url = swagger_css_url
        self.redoc_js_url = redoc_js_url
        self.init_doc()

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
        openapi_bp = Blueprint("openapi", __name__, url_prefix=self.openapi_url_prefix)
        if self.openapi_json_url:
            openapi_bp.add_url_rule(
                self.openapi_json_url, view_func=openapi_json_view, doc_enable=False
            )

        if self.swagger_url:
            openapi_bp.add_url_rule(
                self.swagger_url, view_func=swagger, doc_enable=False
            )

        if self.redoc_url:
            openapi_bp.add_url_rule(self.redoc_url, view_func=redoc, doc_enable=False)

        self.register_blueprint(openapi_bp)
