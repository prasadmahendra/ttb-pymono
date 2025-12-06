#!/usr/bin/env python3

from dotenv import load_dotenv

from starlette.applications import Starlette

from treasury.services.gateways.ttb_api.main.adapter.out.persistence.common.db_config import DbConfig
from treasury.services.gateways.ttb_api.main.application.config.api_service_config import ApiServiceConfig
from treasury.services.gateways.ttb_api.main.application.config.config import GlobalConfig
from treasury.services.gateways.ttb_api.main.application.config.flask_config import FlaskConfig
from treasury.services.gateways.ttb_api.main.application.usecases.security.security_context_factory import \
    SecurityContextFactory
from sqlmodel import SQLModel

load_dotenv()
logger = GlobalConfig.get_logger(__name__)
app: Starlette = ApiServiceConfig.app_init(security_context_factory=SecurityContextFactory())

def main() -> None:
    """Main entry point for the GraphQL API service"""
    logger.info("[starting] service")
    FlaskConfig.serve("treasury.services.gateways.ttb_api.__main__:app", port=8080, workers=4)
    logger.info("[exiting] service")

if __name__ == "__main__":
    main()
