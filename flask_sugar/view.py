from functools import update_wrapper
from re import S
from typing import (
    Optional,
    Callable,
    Any,
    List,
    Dict,
    Tuple,
    NamedTuple,
    TypeVar,
    Union,
    Type,
    Generic,
)

from typing_extensions import Literal
from flask import request
from pydantic import BaseModel, create_model, ValidationError
from pydantic.fields import FieldInfo, ModelField

from flask_sugar import params
from flask_sugar.exceptions import RequestValidationError
from flask_sugar.utils import (
    get_list_value,
    get_path_param_names,
    get_typed_signature,
    get_param_annotation,
    is_list_type,
    is_subclass,
)


class BodyInfo(NamedTuple):
    name: str
    model: Type[BaseModel]
    parameter: params.Body


ParamType = TypeVar("ParamType", params.Param, params.File)


class ParameterInfo(Generic[ParamType]):
    def __init__(self, name: str, is_list: bool, parameter: ParamType) -> None:
        self.name = name
        self.is_list = is_list
        self.parameter = parameter


class View:
    """wrap view_func"""

    def __init__(
        self,
        path: str,
        view_func: Callable,
        doc_enable: bool = True,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "success",
        response_model: Optional[Type[BaseModel]] = None,
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        operation_id: Optional[str] = None,
    ) -> None:
        self.path = path
        self.view_func = view_func
        update_wrapper(self, view_func)  # type:ignore
        self.doc_enable = doc_enable
        self.tags = tags
        self.summary = summary
        self.description = description
        self.response_description = response_description
        self.response_model = response_model
        self.responses = responses
        self.deprecated = deprecated
        self.operation_id = operation_id
        field_definitions: Dict[str, Tuple[Any, FieldInfo]] = {}
        self.ParamModel: Optional[Type[BaseModel]] = None
        self.FormModel: Optional[Type[BaseModel]] = None
        self.parameter_infos: List[ParameterInfo[params.Param]] = []
        self.file_infos: List[ParameterInfo[params.File]] = []
        self.body_info: Optional[BodyInfo] = None

        path_param_names = get_path_param_names(path)
        signature = get_typed_signature(view_func)
        file_definitions: Dict[str, Tuple[Any, FieldInfo]] = {}
        for param_name, param in signature.parameters.items():
            if param.kind in (param.VAR_KEYWORD, param.VAR_POSITIONAL):
                continue
            annotation = get_param_annotation(param)
            if is_subclass(annotation, BaseModel):
                assert (
                    self.body_info is None
                ), "a view_func require only one BaseModel field"
                if param.default == param.empty:
                    parameter = params.Body(...)
                else:
                    assert isinstance(
                        param.default, params.Body
                    ), "body field default value must be instance of params.Body"
                    parameter = param.default

                self.body_info = BodyInfo(
                    name=param_name,
                    model=annotation,
                    parameter=parameter,
                )
                continue
            if isinstance(param.default, params.File):
                # TODO: 加上判断类型是否为(bytes, List[bytes], FileStorage, List[FileStorage])
                self.file_infos.append(
                    ParameterInfo(
                        name=param.name,
                        is_list=is_list_type(annotation),
                        parameter=param.default,
                    )
                )
                file_definitions[param_name] = (bytes, param.default.field_info)
                continue

            if param_name in path_param_names:
                assert (param.default == param.empty) or isinstance(
                    param.default, params.Path
                ), "path param default value must be subclass of params.Path or empty"
                if param.default == param.empty:
                    parameter = params.Path(...)
                else:
                    parameter = param.default
            else:
                if param.default == param.empty:
                    parameter = params.Query(...)
                elif isinstance(param.default, params.Param):
                    parameter = param.default
                else:
                    parameter = params.Query(default=param.default)
            field_definitions[param_name] = (annotation, parameter.field_info)
            self.parameter_infos.append(
                ParameterInfo(
                    name=param_name,
                    is_list=is_list_type(annotation),
                    parameter=parameter,
                )
            )
        if field_definitions:
            self.ParamModel = create_model("ParamModel", **field_definitions)

        if self.file_infos and self.body_info:
            self.FormModel = create_model(
                "FormModel", __base__=self.body_info.model, **file_definitions
            )

    @staticmethod
    def get_value(
        in_: Literal["query", "header", "path", "cookie", "file"],
        alias: str,
        param_name: str,
        is_list: bool,
        kwargs: Dict[str, Any],
    ) -> Any:
        if in_ == "query":
            return request.args.getlist(alias) if is_list else request.args.get(alias)
        if in_ == "header":
            rtn = request.headers.get(alias)
            return get_list_value(rtn) if is_list else rtn
        if in_ == "cookie":
            rtn = request.cookies.get(alias)
            return get_list_value(rtn) if is_list else rtn
        if in_ == "file":
            return request.files.getlist(alias) if is_list else request.files.get(alias)
        return kwargs[param_name]

    def get_request_values(
        self,
        parameter_infos: List[ParameterInfo],
        ParamModel: Type[BaseModel],
        kwargs: Dict[str, Any],
        result_use_alias: bool = True,
    ) -> Dict[str, Any]:
        values = {}
        model_fields: Dict[str, ModelField] = ParamModel.__fields__
        for parameter in parameter_infos:
            model_field = model_fields[parameter.name]
            in_ = parameter.parameter.in_
            alias = model_field.alias
            value = self.get_value(
                in_, alias, parameter.name, parameter.is_list, kwargs
            )
            if value is not None:
                if result_use_alias:
                    values[alias] = value
                else:
                    values[parameter.name] = value
        return values

    def inject_data(
        self, kwargs: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[List[Dict[str, Any]]]]:
        errors: List[List[Dict[str, Any]]] = []
        if self.ParamModel:
            request_values = self.get_request_values(
                self.parameter_infos, self.ParamModel, kwargs
            )
            try:
                param_data = self.ParamModel(**request_values)
                kwargs.update(param_data.dict())
            except ValidationError as e:
                errors.append(e.errors())

        if self.body_info:
            body_values = getattr(request, self.body_info.parameter.request_attr) or {}
            try:
                body_data = self.body_info.model(**body_values)
                kwargs[self.body_info.name] = body_data.dict()
            except ValidationError as e:
                errors.append(e.errors())

        if self.FormModel:
            files = self.get_request_values(
                self.file_infos, self.FormModel, kwargs, False
            )
            kwargs.update(files)

        return kwargs, errors

    def __call__(self, **kwargs) -> Any:
        if self.view_func is None:
            return self.view_func
        cleaned_data, errors = self.inject_data(kwargs)
        if errors:
            raise RequestValidationError(errors)

        return self.view_func(**cleaned_data)

    def __str__(self):
        return f"View(view_func={self.view_func}, doc_enable={self.doc_enable})"
