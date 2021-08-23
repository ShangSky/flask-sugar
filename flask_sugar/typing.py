from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Type, Union

from pydantic import BaseModel

try:
    from typing import get_origin  # type: ignore
except ImportError:  # pragma: no coverage

    def get_origin(tp: Any) -> Optional[Any]:
        return getattr(tp, "__origin__", None)


class MethodsTypingMixin:
    if TYPE_CHECKING:
        from pydantic.typing import AbstractSetIntStr, MappingIntStrAny

        def get(
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
            response_model_include: Union[
                "AbstractSetIntStr", "MappingIntStrAny"
            ] = None,
            response_model_exclude: Union[
                "AbstractSetIntStr", "MappingIntStrAny"
            ] = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
            **options: Any,
        ) -> Callable:
            ...

        post = put = patch = delete = get
