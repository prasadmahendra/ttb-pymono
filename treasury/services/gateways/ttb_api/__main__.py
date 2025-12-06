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

def bootstrap_test_data() -> None:
    # FIXME: only for testing - create tables if not exist
    # We'd never do this in production code. This is just to make it easier to run locally
    # and for this coding example.
    orm_engine = DbConfig.get_orm_engine(local_on_disk=True)
    logger.info("[SQLModel] create_all")
    SQLModel.metadata.create_all(bind=orm_engine)

def main() -> None:
    """Main entry point for the GraphQL API service"""
    logger.info("[starting] service")
    bootstrap_test_data()
    FlaskConfig.serve("treasury.services.gateways.ttb_api.__main__:app", port=8080, workers=4)
    logger.info("[exiting] service")

if __name__ == "__main__":
    main()
