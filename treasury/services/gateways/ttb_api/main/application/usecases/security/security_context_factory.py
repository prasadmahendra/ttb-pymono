from strawberry.types import Info
from starlette.requests import Request

from treasury.services.gateways.ttb_api.main.application.usecases.security.security_context import SecurityContext


class SecurityContextFactory:
    @classmethod
    def from_strawberry_info(cls, info: Info) -> SecurityContext:
        return SecurityContext(
            request=info.context["request"]
        )

    @classmethod
    def from_strawberry_request(cls, request: Request) -> SecurityContext:
        return SecurityContext(
            request=request
        )