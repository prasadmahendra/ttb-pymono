from typing import Any


class GenericException(Exception):
    code: int

    def to_json(self):
        return {"message": str(self), "code": self.code}


class CachingFallbackToDefaultException(GenericException):
    code = 500
    fallback_value: Any

    def __init__(self, fallback_value: Any, *args):
        super().__init__(*args)
        self.fallback_value = fallback_value


class InternalServerException(GenericException):
    code = 500


class BadRequestException(GenericException):
    code = 400


class RateLimitExceededException(GenericException):
    code = 429


class UnauthorizedException(GenericException):
    code = 401


class ServiceUnavailableException(GenericException):
    code = 503


class ForbiddenException(GenericException):
    code = 403


class NotFoundException(GenericException):
    code = 404
