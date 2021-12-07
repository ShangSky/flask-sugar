from inspect import getdoc
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)

from flask import current_app, render_template_string
from pydantic import BaseModel
from pydantic.fields import ModelField, Undefined
from pydantic.schema import (
    TypeModelOrEnum,
    TypeModelSet,
    default_ref_template,
    get_flat_models_from_models,
    get_model_name_map,
    model_process_schema,
    schema,
)

from flask_sugar.constans import ALLOW_METHODS, REF_PREFIX, REF_TEMPLATE
from flask_sugar.templates import redoc_template, swagger_template
from flask_sugar.view import ParameterInfo, View

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
    components: Optional[Dict[str, Union[str, Any]]] = None,
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
    paths, components = collect_paths_components()

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
        components=components,
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


def get_parameters(
    model: Optional[Type[BaseModel]], parameter_infos: List[ParameterInfo]
) -> List[Dict[str, Any]]:
    if not model:
        return []
    model_fields: Dict[str, ModelField] = model.__fields__
    properties = model.schema(ref_template=REF_TEMPLATE)["properties"]
    doc_parameters = []
    for parameter_info in parameter_infos:
        model_field = model_fields[parameter_info.name]
        field_info = parameter_info.parameter.field_info
        doc_parameter = {
            "name": model_field.alias,
            "in": parameter_info.parameter.in_,
            "schema": properties[model_field.alias],
            "required": model_field.required,
        }

        if field_info.description:
            doc_parameter["description"] = field_info.description
        if parameter_info.parameter.examples:
            doc_parameter["examples"] = parameter_info.parameter.examples
        elif parameter_info.parameter.example != Undefined:
            doc_parameter["example"] = parameter_info.parameter.example
        if parameter_info.parameter.deprecated:
            doc_parameter["deprecated"] = parameter_info.parameter.deprecated
        doc_parameters.append(doc_parameter)
    return doc_parameters


def get_flat_models_from_views(view_functions: Iterable[Callable]) -> TypeModelSet:
    models = []
    for view in view_functions:
        if not isinstance(view, View) and getattr(view, "doc_enable"):
            continue
        if view.ParamModel:
            models.append(view.ParamModel)
        if view.body_info or view.FormModel:
            if view.FormModel:
                models.append(view.FormModel)
            else:
                models.append(view.body_info.model)  # type:ignore
        if view.response_model:
            models.append(view.response_model)
    return get_flat_models_from_models(models)


def schema(
    models: TypeModelSet,
    *,
    model_name_map: Dict[TypeModelOrEnum, str],
    by_alias: bool = True,
    title: Optional[str] = None,
    description: Optional[str] = None,
    ref_prefix: Optional[str] = None,
    ref_template: str = default_ref_template,
) -> Dict[str, Any]:
    definitions = {}
    output_schema: Dict[str, Any] = {}
    if title:
        output_schema["title"] = title
    if description:
        output_schema["description"] = description
    for model in models:
        m_schema, m_definitions, m_nested_models = model_process_schema(
            model,
            by_alias=by_alias,
            model_name_map=model_name_map,
            ref_prefix=ref_prefix,
            ref_template=ref_template,
        )
        definitions.update(m_definitions)
        model_name = model_name_map[model]
        definitions[model_name] = m_schema
    if definitions:
        output_schema["definitions"] = definitions
    return output_schema


def collect_paths_components() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    paths = {}
    components = {}
    flat_models = get_flat_models_from_views(current_app.view_functions.values())
    model_name_map = get_model_name_map(flat_models)
    schemas = schema(
        flat_models, model_name_map=model_name_map, ref_prefix=REF_PREFIX
    ).get("definitions", {})
    for rule in current_app.url_map.iter_rules():
        view: View = cast(View, current_app.view_functions[rule.endpoint])
        if not getattr(view, "doc_enable"):
            continue
        action_info = {}
        for method in rule.methods:
            action_info_value = {}
            method: str = method.lower()
            if method not in ALLOW_METHODS:
                continue
            doc_parameters = get_parameters(view.ParamModel, view.parameter_infos)
            if doc_parameters:
                action_info_value["parameters"] = doc_parameters

            tags = view.tags
            if tags:
                action_info_value["tags"] = tags

            summary = view.summary or view.view_func.__name__.replace("_", " ").title()
            if summary:
                action_info_value["summary"] = summary

            description = view.description or getdoc(view)
            if description:
                action_info_value["description"] = description

            deprecated = view.deprecated
            if deprecated:
                action_info_value["deprecated"] = deprecated

            operation_id = view.operation_id or rule.endpoint + "__" + method
            if operation_id:
                action_info_value["operationId"] = operation_id

            action_info[method] = action_info_value
            if view.body_info or view.FormModel:
                if view.FormModel:
                    body_model_name = model_name_map[view.FormModel]
                    media_type = "multipart/form-data"
                else:
                    body_model_name = model_name_map[
                        view.body_info.model  # type:ignore
                    ]
                    media_type = view.body_info.parameter.media_type  # type:ignore

                action_info_value["requestBody"] = {
                    "content": {
                        media_type: {"schema": {"$ref": REF_PREFIX + body_model_name}}
                    },
                    "required": True,
                }
            response_schema = {}
            if view.response_model:
                response_schema["$ref"] = (
                    REF_PREFIX + model_name_map[view.response_model]
                )

            responses: Dict[Union[int, str], Dict[str, Any]] = {
                "200": {
                    "description": view.response_description,
                    "content": {"application/json": {"schema": response_schema}},
                }
            }

            if view.responses:
                responses.update(view.responses)
            action_info_value["responses"] = responses
        paths.setdefault(view.path, {}).update(action_info)

        if schemas:
            components["schemas"] = schemas
    if current_app.security_schemes:
        components["securitySchemes"] = current_app.security_schemes

    return paths, components
