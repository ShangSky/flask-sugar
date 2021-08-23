from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type, Union

from flask import Flask
from pydantic import BaseModel

from flask_sugar.blueprints import Blueprint
from flask_sugar.errorhandlers import validation_error_handler
from flask_sugar.exceptions import RequestValidationError
from flask_sugar.openapi import openapi_json_view, redoc, swagger
from flask_sugar.typing import MethodsTypingMixin
from flask_sugar.utils import convert_path
from flask_sugar.view import View

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny


class Sugar(Flask, MethodsTypingMixin):
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
        security_schemes: Optional[Dict[str, Any]] = None,
        openapi_url_prefix: Optional[str] = None,
        openapi_json_url: str = "/openapi.json",
        swagger_url: str = "/doc",
        redoc_url: str = "/redoc",
        swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js",
        swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css",
        redoc_js_url: str = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        default_validation_errorhandler: Optional[Callable[..., Any]] = None,
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
        self.security_schemes = security_schemes
        self.openapi_url_prefix = openapi_url_prefix
        self.openapi_json_url = openapi_json_url
        self.swagger_url = swagger_url
        self.redoc_url = redoc_url
        self.openapi_version = "3.0.2"
        self.swagger_js_url = swagger_js_url
        self.swagger_css_url = swagger_css_url
        self.redoc_js_url = redoc_js_url
        error_handler = (
            default_validation_errorhandler
            if default_validation_errorhandler is not None
            else validation_error_handler
        )
        self.register_error_handler(RequestValidationError, error_handler)

        self.init_doc()

    def add_url_rule(
        self,
        rule: str,
        endpoint: Optional[str] = None,
        view_func: Optional[Callable] = None,
        provide_automatic_options: Optional[bool] = None,
        doc_enable: bool = True,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_model: Optional[Type[BaseModel]] = None,
        response_description: str = "success",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        operation_id: Optional[str] = None,
        response_model_include: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        response_model_exclude: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        **options: Any,
    ) -> None:
        path = convert_path(rule)
        assert view_func, "view_func can't be None"
        view = View(
            path=path,
            view_func=view_func,
            doc_enable=doc_enable,
            tags=tags,
            summary=summary,
            description=description,
            response_description=response_description,
            response_model=response_model,
            responses=responses,
            deprecated=deprecated,
            operation_id=operation_id,
        )
        super().add_url_rule(rule, endpoint, view, provide_automatic_options, **options)

    def init_doc(self):
        openapi_bp = Blueprint("openapi", __name__, url_prefix=self.openapi_url_prefix)
        if self.openapi_json_url:
            openapi_bp.add_url_rule(
                self.openapi_json_url, view_func=openapi_json_view, doc_enable=False
            )

        if self.openapi_json_url and self.swagger_url:
            openapi_bp.add_url_rule(
                self.swagger_url, view_func=swagger, doc_enable=False
            )

        if self.openapi_json_url and self.redoc_url:
            openapi_bp.add_url_rule(self.redoc_url, view_func=redoc, doc_enable=False)

        self.register_blueprint(openapi_bp)
