import tempfile
from sqlalchemy import Engine, create_engine, Insert
from sqlalchemy.dialects import postgresql
from sqlmodel import SQLModel

from treasury.services.gateways.ttb_api.main.application.config import config
from treasury.services.gateways.ttb_api.main.application.config.config import GlobalConfig


class DbConfig:


    _postgres_user = config.PGUSER or "my_db_user"
    _postgres_host = config.PGHOST or "127.0.0.1"
    _postgres_db = config.PGDATABASE or "neondb"
    _postgres_port = config.AWS_AURORA_PSQL_PORT or "5432"
    _postgres_password = config.PGPASSWORD or ""

    # # Parameters for constructing your own connection string
    # PGHOST=ep-curly-sunset-a4i2ngj5-pooler.us-east-1.aws.neon.tech
    # PGHOST_UNPOOLED=ep-curly-sunset-a4i2ngj5.us-east-1.aws.neon.tech
    # PGUSER=neondb_owner
    # PGDATABASE=neondb
    # PGPASSWORD=npg_XhRATGBog0f4

    _orm_engine_cache = {}
    _logger = GlobalConfig.get_logger(__name__)

    @classmethod
    def bootstrap_test_data(cls, orm_engine) -> None:
        # FIXME: only for testing - create tables if not exist
        # We'd never do this in production code. This is just to make it easier to run locally
        # and for this coding example.
        cls._logger.info("[SQLModel] create_all")
        SQLModel.metadata.create_all(bind=orm_engine)

    @classmethod
    def get_orm_engine(
            cls,
            in_memory: bool = False, # default to in_memory for this coding exercise purposes only
            local_on_disk: bool = False,
            local_db_file_name: str = "treasury_db_local.db"  # for testing purposes only!
    ) -> Engine:

        echo = False
        org_engines_cache_key = f"{in_memory}_{local_on_disk}_{local_db_file_name}"
        if cls._orm_engine_cache.get(org_engines_cache_key):
            return cls._orm_engine_cache[org_engines_cache_key]
        if local_on_disk and in_memory:
            raise ValueError("Cannot have both local_on_disk and in_memory set to True")

        if local_on_disk:
            temp_folder_dir = tempfile.gettempdir()
            cls._logger.info(f"sqlite:///{temp_folder_dir}/{local_db_file_name}")
            engine: Engine = create_engine(
                f"sqlite:///{temp_folder_dir}/{local_db_file_name}",
                echo=echo,
                echo_pool=True,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=5
            )
            cls.bootstrap_test_data(engine)
        elif in_memory:
            engine: Engine = create_engine(
                "sqlite:///:memory:",
                echo=echo,
                echo_pool=True,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=5
            )
        else:
            engine: Engine = create_engine(
                cls.get_sql_connection_string(),
                echo=echo,
                echo_pool=True,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=5
            )
        cls._orm_engine_cache[org_engines_cache_key] = engine
        return engine

    @staticmethod
    def insert_if_not_exists(model: SQLModel) -> Insert:

        # the postgresql.insert function is used to generate an INSERT statement with an ON CONFLICT DO NOTHING clause.
        # note that sqlite also supports ON CONFLICT DO NOTHING, so this works with both database types.
        statement = (
            postgresql.insert(model.__class__).values(**model.model_dump(exclude_unset=True)).on_conflict_do_nothing()
        )
        return statement

    @staticmethod
    def upsert(
            model: SQLModel,
            on_conflict_do_set: dict,
            index_elements: list[str] = None,
            constraint: str = None
    ) -> Insert:
        statement = (
            postgresql.insert(model.__class__).values(**model.model_dump(exclude_unset=True)).on_conflict_do_update(
                set_=on_conflict_do_set,
                index_elements=index_elements,
                constraint=constraint
            )
        )
        return statement

    @staticmethod
    def insert(model: SQLModel) -> Insert:
        statement = (
            postgresql.insert(model.__class__).values(**model.model_dump(exclude_unset=True))
        )
        return statement

    @classmethod
    def get_sql_connection_string(cls, admin_mode: bool = False):

        postgres_password = cls._postgres_password

        # host/port connection
        # postgresql+pg8000://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sql_connection = f"postgresql+psycopg2://{cls._postgres_user}:{postgres_password}@{cls._postgres_host}:{cls._postgres_port}/{cls._postgres_db}?sslmode=require"
        cls._logger.info(f"Connecting to database {sql_connection.replace(postgres_password, '********')}")

        return sql_connection
