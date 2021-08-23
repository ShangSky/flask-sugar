from typing import Any, Callable, Iterable, Type

from werkzeug.datastructures import FileStorage


class UploadFile(FileStorage):
    @classmethod
    def __get_validators__(cls: Type["UploadFile"]) -> Iterable[Callable[..., Any]]:
        yield cls.validate

    @classmethod
    def validate(cls: Type["UploadFile"], v: Any) -> Any:
        if not isinstance(v, FileStorage):
            raise ValueError(f"Expected UploadFile, received: {type(v)}")
        return v

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(format="binary", type="string")
