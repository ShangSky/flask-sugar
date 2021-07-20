from flask import current_app, render_template_string

from typing import Optional, List, Dict, Union, Any, cast

from flask_sugar.templates import swagger_template, redoc_template
from flask_sugar.view import View
from flask_sugar.utils import convert_path


def get_openapi_json(
        openapi_version: str,
        title: str,
        version: str,
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
    if servers:
        source["servers"] = servers
    if paths:
        source["paths"] = paths
    if components:
        source["components"] = components
    return source


def openapi_json_view():
    openapi_version: str = current_app.config.get("SUGAR_OPENAPI_VERSION", "3.0.2")
    title: str = current_app.config.get("SUGAR_TITLE", "FlaskSugar")
    version: str = current_app.config.get("SUGAR_VERSION", "0.1.0")
    description: Optional[str] = current_app.config.get("SUGAR_DESCRIPTION", "")
    terms_service: Optional[str] = current_app.config.get("SUGAR_TERMS_SERVICE")
    contact: Optional[Dict[str, str]] = current_app.config.get("SUGAR_CONTACT")
    license_: Optional[Dict[str, str]] = current_app.config.get("SUGAR_LICENSE")
    servers: Optional[List[Dict[str, Union[str, Any]]]] = current_app.config.get(
        "SUGAR_SERVERS"
    )
    paths = collect_paths()
    components = {}

    return get_openapi_json(
        openapi_version=openapi_version,
        title=title,
        version=version,
        description=description,
        terms_service=terms_service,
        contact=contact,
        license_=license_,
        servers=servers,
        paths=paths
    )


def swagger():
    openapi_json_url: str = current_app.config.get("SUGAR_OPENAPI_JSON_URL", "/openapi.json")
    title: str = current_app.config.get("SUGAR_TITLE", "FlaskSugar")
    swagger_js_url: str = current_app.config.get(
        "SUGAR_SWAGGER_JS_URL",
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js",
    )
    swagger_css_url: str = current_app.config.get(
        "SUGAR_SWAGGER_CSS_URL",
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css",
    )

    return render_template_string(
        swagger_template,
        openapi_json_url=openapi_json_url,
        title=title + " Swagger",
        swagger_js_url=swagger_js_url,
        swagger_css_url=swagger_css_url,
    )


def redoc():
    openapi_json_url: str = current_app.config.get("SUGAR_OPENAPI_JSON_URL", "/openapi.json")
    title: str = current_app.config.get("SUGAR_TITLE", "FlaskSugar")
    redoc_js_url: str = current_app.config.get(
        "SUGAR_REDOC_JS_URL",
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )
    return render_template_string(
        redoc_template,
        openapi_json_url=openapi_json_url,
        title=title + " Redoc",
        redoc_js_url=redoc_js_url,
    )


def collect_paths() -> Dict[str, Any]:
    allow_methods = {"get", "post", "put", "delete", "patch"}
    paths = {}
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue
        view: View = cast(View, current_app.view_functions[rule.endpoint])
        if not getattr(view, 'doc_enable'):
            continue
        path = convert_path(rule.rule)
        action_info = {}
        for method in rule.methods:
            method: str = method.lower()
            if method in allow_methods:
                action_info[method] = {}

        paths[path] = action_info
    return paths
