import uuid
from typing import Optional

from treasury.services.gateways.ttb_api.main.application.models.domain.entity_descriptor import EntityDescriptor
from treasury.services.gateways.ttb_api.main.application.models.domain.user import User


class UserManagementService:

    random_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    random_name = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Cameron"]
    _TEST_USER = User(
        id=uuid.uuid4(),
        name=random_name[uuid.uuid4().int % len(random_name)],
        email=random_email
    )

    def __init__(self) -> None:
        pass

    def get_user_by_authenticated_entity(
            self,
            entity: EntityDescriptor
    ) -> Optional[User]:
        # TODO - This is hard coded for now to always return the same user
        return self._TEST_USER
