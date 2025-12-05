from typing import Union

from strawberry.asgi import GraphQL

from starlette.requests import Request
from starlette.responses import (
    Response,
)
from starlette.websockets import WebSocket
from strawberry.http.typevars import (
    Context,
)

from treasury.services.gateways.ttb_api.main.application.usecases.security.security_context_factory import \
    SecurityContextFactory


class GraphQlWithSecurityContext(GraphQL):

    def __init__(self, *args, security_context_factory: SecurityContextFactory, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._security_context_factory = security_context_factory

    async def get_context(
            self,
            request: Union[Request, WebSocket],
            response: Union[Response, WebSocket]
    ) -> Context:
        return {
            "request": request,
            "response": response,
            "security_context": self._security_context_factory.from_strawberry_request(request)
        }  # type: ignore