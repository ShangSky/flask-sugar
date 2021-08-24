from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Type, Union

from pydantic import BaseModel

try:
    from typing import get_origin  # type: ignore
except ImportError:  # pragma: no coverage

    def get_origin(tp: Any) -> Optional[Any]:
        return getattr(tp, "__origin__", None)
