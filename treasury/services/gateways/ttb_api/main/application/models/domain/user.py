import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.sql.schema import Index
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        Index("email_idx", "email"),
    )

    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    email: str = Field(nullable=False, unique=True)
    name: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)
    created_by_entity: str = Field(nullable=False)
    created_by_entity_id: str = Field(nullable=False)
    created_by_entity_domain: str = Field(nullable=False)
    updated_by_entity: str = Field(nullable=False)
    updated_by_entity_id: Optional[str] = Field(default=None, nullable=True)
    updated_by_entity_domain: Optional[str] = Field(default=None, nullable=True)