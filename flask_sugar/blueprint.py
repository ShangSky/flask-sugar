from typing import Optional, Callable, Any, List, Type, Dict, Union, TYPE_CHECKING

from flask import Blueprint as _Blueprint
from pydantic import BaseModel


class Blueprint(_Blueprint):
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
        **options: Any,
    ) -> None:
        """Like :meth:`Flask.add_url_rule` but for a blueprint.  The endpoint for
        the :func:`url_for` function is prefixed with the name of the blueprint.
        """
        if endpoint and "." in endpoint:
            raise ValueError("'endpoint' may not contain a dot '.' character.")

        if view_func and hasattr(view_func, "__name__") and "." in view_func.__name__:
            raise ValueError("'view_func' name may not contain a dot '.' character.")

        self.record(
            lambda s: s.add_url_rule(
                rule,
                endpoint,
                view_func,
                provide_automatic_options=provide_automatic_options,
                doc_enable=doc_enable,
                tags=tags,
                summary=summary,
                description=description,
                response_model=response_model,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                operation_id=operation_id,
                **options,
            )
        )

    if TYPE_CHECKING:

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
            **options: Any,
        ) -> Callable:
            ...

        post = put = patch = delete = get
