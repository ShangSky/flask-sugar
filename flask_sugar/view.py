from functools import update_wrapper
from typing import Optional, Callable, Any, List

from pydantic import BaseModel

from flask_sugar import params
from flask_sugar.utils import get_path_param_names, get_typed_signature, get_param_annotation


class ArgInfo:
    def __init__(self, name: str, annotation: Any, field_info: Optional[params.Param] = None):
        self.name = name
        self.annotation = annotation
        self.field_info = field_info


class View:
    """wrap view_func"""

    def __init__(
        self,
        path: Optional[str],
        view_func: Optional[Callable] = None,
        doc_enable: bool = True,
        endpoint: Optional[str] = None,
    ) -> None:
        self.path = path
        self.view_func = view_func
        update_wrapper(self, view_func)  # type:ignore
        self.doc_enable = doc_enable
        self.parameters = {}
        path_param_names = get_path_param_names(path)
        signature = get_typed_signature(view_func)
        self.arg_infos: List[ArgInfo] = []
        for param_name, param in signature.parameters.items():
            if param.kind in (param.VAR_KEYWORD, param.VAR_POSITIONAL):
                continue
            name = param_name
            annotation = get_param_annotation(param)
            field_info = None
            if param_name in path_param_names:
                assert (param.default == param.empty) or isinstance(
                    param.default, params.Path
                ), "path param default value must be subclass of params.Path or empty"
                if param.default == param.empty:
                    field_info = params.Path(...)
                else:
                    field_info = param.default
            else:
                if param.default == param.empty:
                    if not (annotation in [list, List] or isinstance(param.annotation, BaseModel)):
                        field_info = params.Query(...)
                elif isinstance(param.default, params.Param):
                    field_info = param.default
                else:
                    field_info = params.Query(default=param.default)
            self.arg_infos.append(ArgInfo(name=name, annotation=annotation, field_info=field_info))
        print(self.arg_infos)

    def __call__(self, *args, **kwargs) -> Any:
        if self.view_func is None:
            return self.view_func
        return self.view_func(*args, **kwargs)

    def __str__(self):
        return f"View(view_func={self.view_func}, doc_enable={self.doc_enable})"
