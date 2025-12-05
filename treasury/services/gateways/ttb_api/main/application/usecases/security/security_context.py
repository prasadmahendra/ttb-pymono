import uuid
from functools import wraps
from typing import Optional, List, Set

from starlette.datastructures import Headers
from starlette.requests import Request
from strawberry.types import Info

from pydantic import BaseModel

from treasury.services.gateways.ttb_api.main.application.config.config import GlobalConfig
from treasury.services.gateways.ttb_api.main.application.models.domain.entity_descriptor import EntityDescriptor
from treasury.services.gateways.ttb_api.main.application.models.domain.iam_role_permissions import IamRolePermissions


class _AuthHeaderVerification(BaseModel):
    pass


class _AuthorizationHeader(BaseModel):
    header_type: Optional[str] = None
    secret: Optional[str] = None


class SecurityContext:
    _logger = GlobalConfig.get_logger(__name__)

    def __init__(self, request: Request) -> None:
        self._request = request
        self._is_org_scope_debug_log_entries = []
        self._verification: Optional[_AuthHeaderVerification] = None

    def get_headers(self) -> Headers:
        return self._request.headers

    def verify_bearer_token_once(self) -> Optional[_AuthHeaderVerification]:
        if self._verification:
            return self._verification
        self._verification = self.verify_bearer_token()
        return self._verification

    def get_authenticated_entity_from_security_ctx(self) -> Optional[EntityDescriptor]:
        # TODO - Add support auth later
        return EntityDescriptor.of_anonymous()

    def verify_bearer_token(self) -> Optional[_AuthHeaderVerification]:
        # TODO - Add support auth later
        return None

    def role_permissions_required(
            self,
            permissions: List[IamRolePermissions]
    ):
        """
        Decorator to enforce role-based permissions on a function.
        Checks to see if the authenticated entity has the required permissions.
        :param permissions:
        :return:
        """

        def wrapper(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                # TODO - Implement role permission checks here
                return f(*args, **kwargs)

            return wrapped

        return wrapper

    def get_x_forwarded_for_header(self) -> Optional[str]:
        try:
            request_headers: Headers = self.get_headers()
            x_forwarded_for_header: str = request_headers.get("x-forwarded-for")
            return x_forwarded_for_header
        except Exception as e:
            self._logger.info(f"Error getting x-forwarded-for header error={e}", exc_info=True)
            return None

    def get_user_agent_header(self) -> Optional[str]:  # pragma: no cover
        try:
            request_headers: Headers = self.get_headers()
            user_agent_header: str = request_headers.get("User-Agent")
            return user_agent_header
        except Exception as e:
            self._logger.info(f"Error getting user-agent header error={e}", exc_info=True)
            return None

    @classmethod
    def from_info(cls, info: Info) -> 'SecurityContext':
        security_context: SecurityContext = info.context['security_context']
        security_context.verify_bearer_token_once()
        return security_context
