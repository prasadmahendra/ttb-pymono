import os
import unittest
from unittest.mock import MagicMock

from starlette.applications import Starlette
from starlette.testclient import TestClient

from treasury.services.gateways.ttb_api.main.application.usecases.security.security_context import SecurityContext
from treasury.services.gateways.ttb_api.main.application.usecases.security.security_context_factory import \
    SecurityContextFactory
from treasury.services.gateways.ttb_api.test.testing.security_context_test_utils import SecurityContextTestUtils


class BaseApiServiceTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        if 'api_service_config_base' in kwargs:
            api_service_config_base = kwargs.pop('api_service_config_base')
            self._api_service_config_base = api_service_config_base
        super().__init__(*args, **kwargs)

        self._security_context_factory = MagicMock(spec=SecurityContextFactory)

        self._security_context: SecurityContext = MagicMock(spec=SecurityContext)
        self._security_context_factory.from_strawberry_info.return_value = self._security_context
        self._security_context_factory.from_strawberry_request.return_value = self._security_context
        os.environ.setdefault('ENV_IS_LOCAL', 'true')

    def setUp(self) -> None:
        self._client = self._get_test_client()

    def _create_app(self) -> Starlette:
        return self._api_service_config_base.app_init(
            security_context_factory=self._security_context_factory
        )

    def _get_test_client(self) -> TestClient:
        app = self._create_app()
        client = TestClient(app)
        return client

    def get(self, *args, **kwargs):
        resp = self._client.get(*args, **kwargs)
        return resp

    def post(self, *args, **kwargs):
        resp = self._client.post(*args, **kwargs)
        return resp

    def put(self, *args, **kwargs):
        resp = self._client.put(*args, **kwargs)
        return resp

    def delete(self, *args, **kwargs):
        resp = self._client.delete(*args, **kwargs)
        return resp

    def patch(self, *args, **kwargs):
        resp = self._client.patch(*args, **kwargs)
        return resp
