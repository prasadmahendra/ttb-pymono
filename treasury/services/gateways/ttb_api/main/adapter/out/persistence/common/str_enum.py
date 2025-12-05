from enum import Enum

from sqlalchemy import TypeDecorator, String


# Based on:
# https://michaelcho.me/article/using-python-enums-in-sqlalchemy-models/
class StrEnum(TypeDecorator):
    """Stores an enum by its string value vs. name"""
    impl = String
    cache_ok = True

    def __init__(self, enumtype, *args, **kwargs):
        super(StrEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value: str | Enum, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return value.value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self._enumtype(value)
