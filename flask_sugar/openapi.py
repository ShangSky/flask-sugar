from flask import current_app, render_template_string

from typing import Optional, List, Dict, Union, Any, cast, TYPE_CHECKING

from flask_sugar.templates import swagger_template, redoc_template
from flask_sugar.view import View
from flask_sugar.utils import convert_path

if TYPE_CHECKING:
    from flask_sugar.app import Sugar

    current_app: Sugar


def get_openapi_json(
    openapi_version: str,
    title: str,
    version: str,
    tags: Optional[List[Dict[str, Any]]] = None,
    description: Optional[str] = "",
    terms_service: Optional[str] = None,
    contact: Optional[Dict[str, str]] = None,
    license_: Optional[Dict[str, str]] = None,
    servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
    paths: Optional[Dict[str, Union[str, Any]]] = None,
    components: Optional[List[Dict[str, Union[str, Any]]]] = None,
) -> Dict[str, Any]:
    info: Dict[str, Any] = {"title": title, "version": version}
    if description:
        info["description"] = description
    if terms_service:
        info["termsOfService"] = terms_service
    if contact:
        info["contact"] = contact
    if license_:
        info["license"] = license_
    source = {
        "openapi": openapi_version,
        "info": info,
    }
    if tags:
        source["tags"] = tags
    if servers:
        source["servers"] = servers
    if paths:
        source["paths"] = paths
    if components:
        source["components"] = components
    return source


def openapi_json_view() -> Dict[str, Any]:
    paths = collect_paths()
    components = {}

    return get_openapi_json(
        openapi_version=current_app.openapi_version,
        title=current_app.title,
        version=current_app.doc_version,
        tags=current_app.tags,
        description=current_app.description,
        terms_service=current_app.terms_service,
        contact=current_app.contact,
        license_=current_app.license_,
        servers=current_app.servers,
        paths=paths,
    )


def swagger() -> str:
    return render_template_string(
        swagger_template,
        openapi_json_url=current_app.openapi_json_url,
        title=current_app.title + " Swagger",
        swagger_js_url=current_app.swagger_js_url,
        swagger_css_url=current_app.swagger_css_url,
    )


def redoc() -> str:
    return render_template_string(
        redoc_template,
        openapi_json_url=current_app.openapi_json_url,
        title=current_app.title + " Redoc",
        redoc_js_url=current_app.redoc_js_url,
    )


def collect_paths() -> Dict[str, Any]:
    allow_methods = {"get", "post", "put", "delete", "patch"}
    paths = {}
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue
        view: View = cast(View, current_app.view_functions[rule.endpoint])
        if not getattr(view, "doc_enable"):
            continue
        path = convert_path(rule.rule)
        action_info = {}
        for method in rule.methods:
            method: str = method.lower()
            if method in allow_methods:
                action_info[method] = {}

        paths[path] = action_info
    return paths
