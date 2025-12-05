import uuid
from typing import Optional

from pydantic import BaseModel

class EntityDescriptor(BaseModel):

    type: Optional[str] = None
    id: Optional[str] = None
    org_id: Optional[str] = None

    @classmethod
    def of_tools(cls, id: str, org_id: Optional[uuid.UUID] = None) -> "EntityDescriptor":
        return cls(type="tools", id=id, org_id=str(org_id) if org_id else "na")

    @classmethod
    def of_user(cls, id: str, org_id: Optional[uuid.UUID] = None) -> "EntityDescriptor":
        return cls(type="user", id=id, org_id=str(org_id) if org_id else "na")

    @classmethod
    def of_organization(cls, id: uuid.UUID, org_id: Optional[uuid.UUID] = None) -> "EntityDescriptor":
        return cls(type="organization", id=str(id), org_id=str(org_id) if org_id else str(id))

    @classmethod
    def of_system(cls) -> "EntityDescriptor":
        return cls(type="system", id="system", org_id="system")

    @classmethod
    def of_tests(cls) -> "EntityDescriptor":
        return cls(type="test", id="test", org_id="test")

    @classmethod
    def of_anonymous(cls) -> "EntityDescriptor":
        return cls(type="anonymous", id="anonymous", org_id="anonymous")

