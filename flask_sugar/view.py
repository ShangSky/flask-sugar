from functools import update_wrapper
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from flask import request
from flask.typing import ResponseReturnValue
from pydantic import (
    BaseModel,
    ValidationError,
    create_model,
    create_model_from_typeddict,
)
from pydantic.fields import FieldInfo, ModelField
from typing_extensions import Literal
from werkzeug.datastructures import ImmutableMultiDict

from flask_sugar import params
from flask_sugar.datastructures import UploadFile
from flask_sugar.exceptions import RequestValidationError
from flask_sugar.utils import (
    get_list_value,
    get_param_annotation,
    get_path_param_names,
    get_typed_signature,
    is_list_type,
    is_subclass,
    is_typed_dict,
)

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny


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
        response_model_include: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        response_model_exclude: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
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
        self.ParamModel: Optional[Type[BaseModel]] = None
        self.FormModel: Optional[Type[BaseModel]] = None
        self.FileModel: Optional[Type[BaseModel]] = None
        self.parameter_infos: List[ParameterInfo[params.Param]] = []
        self.file_infos: List[ParameterInfo[params.File]] = []
        self.body_info: Optional[BodyInfo] = None
        self.response_model_include = response_model_include
        self.response_model_exclude = response_model_exclude
        self.response_model_by_alias = response_model_by_alias
        self.response_model_exclude_unset = response_model_exclude_unset
        self.response_model_exclude_defaults = response_model_exclude_defaults
        self.response_model_exclude_none = response_model_exclude_none

        field_definitions: Dict[str, Tuple[Any, FieldInfo]] = {}
        path_param_names = get_path_param_names(path)
        signature = get_typed_signature(view_func)
        file_definitions: Dict[str, Tuple[Any, FieldInfo]] = {}
        if not response_model:
            if is_typed_dict(signature.return_annotation):
                self.response_model = create_model_from_typeddict(
                    signature.return_annotation
                )
            elif is_subclass(signature.return_annotation, BaseModel):
                self.response_model = signature.return_annotation

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
                annotation = param.annotation
                if param.annotation == param.empty:
                    annotation = UploadFile
                is_list = is_list_type(annotation)
                self.file_infos.append(
                    ParameterInfo(
                        name=param.name,
                        is_list=is_list,
                        parameter=param.default,
                    )
                )
                file_definitions[param_name] = (annotation, param.default.field_info)
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

        if self.file_infos:
            if self.body_info:
                assert isinstance(
                    self.body_info.parameter, params.Form
                ), "file field cant not coexist with body field"
                base_model = self.body_info.model
            else:
                base_model = None
            self.FileModel = create_model("FileModel", **file_definitions)
            self.FormModel = create_model(
                "FormModel", __base__=base_model, **file_definitions
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
            if isinstance(body_values, ImmutableMultiDict):
                body_values = body_values.to_dict()
            try:
                kwargs[self.body_info.name] = self.body_info.model(**body_values)
            except ValidationError as e:
                errors.append(e.errors())

        if self.FileModel:
            files = self.get_request_values(
                self.file_infos, self.FileModel, kwargs, False
            )

            try:
                file_model = self.FileModel(**files)
                kwargs.update(file_model.dict())
            except ValidationError as e:
                errors.append(e.errors())

        return kwargs, errors

    def create_response(
        self, response: Union[ResponseReturnValue, BaseModel]
    ) -> ResponseReturnValue:
        if isinstance(response, BaseModel):
            return response.dict()
        if isinstance(response, dict) and self.response_model:
            return self.response_model(**response).dict(
                include=self.response_model_include,
                exclude=self.response_model_exclude,
                by_alias=self.response_model_by_alias,
                exclude_unset=self.response_model_exclude_unset,
                exclude_defaults=self.response_model_exclude_defaults,
                exclude_none=self.response_model_exclude_none,
            )
        return response

    def __call__(self, **kwargs) -> Any:
        if self.view_func is None:
            return self.view_func
        cleaned_data, errors = self.inject_data(kwargs)
        if errors:
            raise RequestValidationError(errors)
        response = self.view_func(**cleaned_data)
        return self.create_response(response)

    def __str__(self):
        return f"View(view_func={self.view_func}, doc_enable={self.doc_enable})"
