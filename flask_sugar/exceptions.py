from typing import Any, Dict, List


class RequestValidationError(Exception):
    def __init__(self, errors: List[Dict[str, Any]]):
        self.errors = errors
