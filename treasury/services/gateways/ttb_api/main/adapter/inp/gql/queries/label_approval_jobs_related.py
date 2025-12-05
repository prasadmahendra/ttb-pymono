import strawberry
import uuid
from typing import Optional

from strawberry import Info

from treasury.services.gateways.ttb_api.main.adapter.inp.gql.queries.common import QueriesCommon
from treasury.services.gateways.ttb_api.main.application.models.gql.label_approvals.list_label_approval_jobs_request import (
    ListLabelApprovalJobsInput,
    ListLabelApprovalJobsResponse
)
from treasury.services.gateways.ttb_api.main.application.models.mappers.object_mapper import ObjectMapper


@strawberry.type
class LabelApprovalJobsRelated(QueriesCommon):
    @strawberry.field
    def hello(self, info: Info, name: Optional[str] = None) -> str:
        """A simple hello world query"""
        if name:
            return f"Hello, {name}!"
        return "Hello, world!"

    @strawberry.field
    def list_label_approval_jobs(self, info: Info, input: ListLabelApprovalJobsInput) -> ListLabelApprovalJobsResponse:
        """List label approval jobs with optional filters and pagination"""
        return QueriesCommon._label_approval_jobs_service.list_label_approval_jobs(
            info=info,
            input=input
        )
