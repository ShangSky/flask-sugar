from functools import update_wrapper
from typing import Optional, Callable, Any, List, Dict, Tuple, NamedTuple, Union, Type

from flask import request
from pydantic import BaseModel, create_model, ValidationError
from pydantic.fields import FieldInfo, ModelField

from flask_sugar import params
from flask_sugar.params import ParamTypes
from flask_sugar.utils import (
    get_path_param_names,
    get_typed_signature,
    get_param_annotation,
)


class ParameterInfo(NamedTuple):
    name: str
    parameter: params.Param


class View:
    """wrap view_func"""

    def __init__(
        self,
        path: Optional[str],
        view_func: Optional[Callable] = None,
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
        path_param_names = get_path_param_names(path)
        signature = get_typed_signature(view_func)
        field_definitions: Dict[str, Tuple[Any, FieldInfo]] = {}
        self.param_model: Optional[Type[BaseModel]] = None
        self.parameters: List[ParameterInfo] = []
        self.body_model: Optional[Type[BaseModel]] = None
        for param_name, param in signature.parameters.items():
            if param.kind in (param.VAR_KEYWORD, param.VAR_POSITIONAL):
                continue
            annotation = get_param_annotation(param)
            try:
                if issubclass(param.annotation, BaseModel):
                    assert (
                        self.body_model is None
                    ), "a view_func require only one BaseModel field"
                    self.body_model = param.annotation
                    continue
            except TypeError:
                pass
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
            self.parameters.append(ParameterInfo(name=param_name, parameter=parameter))
        if field_definitions:
            self.param_model = create_model("ParamModel", **field_definitions)

    @staticmethod
    def get_value(
        in_: ParamTypes, alias: str, param_name: str, kwargs: Dict[str, Any]
    ) -> Any:
        if in_ == "query":
            return request.args.get(alias)
        if in_ == "header":
            return request.headers.get(alias)
        if in_ == "cookie":
            return request.cookies.get(alias)
        return kwargs[param_name]

    def __call__(self, **kwargs) -> Any:
        if self.view_func is None:
            return self.view_func
        if not self.param_model:
            # TODO
            return self.view_func(**kwargs)
        model_fields: Dict[str, ModelField] = self.param_model.__fields__
        values = {}
        for parameter in self.parameters:
            model_field = model_fields[parameter.name]
            in_ = parameter.parameter.in_
            alias = model_field.alias
            value = self.get_value(in_, alias, parameter.name, kwargs)
            if value is not None:
                values[alias] = value
        try:
            data = self.param_model(**values)
        except ValidationError as e:
            print(e.errors())
        return self.view_func(**data.dict())

    def __str__(self):
        return f"View(view_func={self.view_func}, doc_enable={self.doc_enable})"
