import strawberry
from strawberry.asgi import GraphQL

from starlette.middleware.cors import CORSMiddleware
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request

from treasury.services.gateways.ttb_api.main.adapter.inp.gql.error_handler import ErrorHandlerExtension
from treasury.services.gateways.ttb_api.main.adapter.inp.gql.mutation import Mutation
from treasury.services.gateways.ttb_api.main.adapter.inp.gql.query import Query
from treasury.services.gateways.ttb_api.main.application.config import config
from treasury.services.gateways.ttb_api.main.application.config.config import GlobalConfig
from treasury.services.gateways.ttb_api.main.application.usecases.security.graphql_with_security_context import \
    GraphQlWithSecurityContext
from treasury.services.gateways.ttb_api.main.application.usecases.security.security_context_factory import \
    SecurityContextFactory


class ApiServiceConfig:

    logger = GlobalConfig.get_logger(__name__)

    @staticmethod
    async def health_check(request: Request) -> JSONResponse:
        ApiServiceConfig.logger.info("Health check started.")
        return JSONResponse({"status": "healthy"}, status_code=200)

    @classmethod
    def app_init(cls, security_context_factory: SecurityContextFactory) -> Starlette:

        # Create schema with custom error handling extension
        schema = strawberry.Schema(
            query=Query,
            mutation=Mutation,
            extensions=[ErrorHandlerExtension]
        )

        # Create ASGI app
        graphql_app: GraphQL = GraphQlWithSecurityContext(
            schema=schema,
            security_context_factory=security_context_factory
        )

        allowed_origins_str_list = config.ALLOWED_ORIGINS or "*"
        allow_origins: list[str] = [origin.strip() for origin in allowed_origins_str_list.split(",")]
        cls.logger.info(f"CORS allowed origins={allow_origins}")

        # Wrap with CORS middleware
        app = Starlette()
        app.add_middleware(
            CORSMiddleware,
            #  allow_origins=["*"] combined with allow_credentials=True, which is not allowed by browsers -
            #  when credentials are enabled, you must specify explicit origins
            allow_origins=allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.add_route("/health", cls.health_check, methods=["GET"])
        app.add_route("/graphql", graphql_app, methods=["GET", "POST", "OPTIONS"])
        app.add_route("/graphql/", graphql_app, methods=["GET", "POST", "OPTIONS"])  # Handle trailing slash
        return app

    @property
    def version(self):
        return config.SERVICE_VERSION or "0.0.1"
