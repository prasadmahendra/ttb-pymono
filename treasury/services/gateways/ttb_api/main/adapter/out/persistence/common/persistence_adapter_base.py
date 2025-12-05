from abc import ABC
from contextlib import contextmanager
from typing import Generator, Any

from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from treasury.services.gateways.ttb_api.main.adapter.out.persistence.common.db_config import DbConfig


class PersistenceAdapterBase(ABC):
    def __init__(self, orm_engine: Engine = None) -> None:
        self._orm_engine_lazy: Engine = orm_engine

    @property
    def _orm_engine(self) -> Engine:
        if self._orm_engine_lazy is None:
            self._orm_engine_lazy = DbConfig.get_orm_engine()
        return self._orm_engine_lazy

    @contextmanager
    def transaction(self) -> Generator[Session, Any, None]:
        with Session(self._orm_engine, expire_on_commit=False, autocommit=False) as session:
            yield session
