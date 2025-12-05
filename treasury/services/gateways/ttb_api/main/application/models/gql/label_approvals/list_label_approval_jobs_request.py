from typing import Optional

import strawberry

from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import LabelApprovalStatus
from treasury.services.gateways.ttb_api.main.application.models.dto.label_approval_job_dto import LabelApprovalJobDTO


@strawberry.input
class ListLabelApprovalJobsInput:
    """Input for listing label approval jobs with filters and pagination"""
    brand_name_like: Optional[str] = None
    status: Optional[LabelApprovalStatus] = None
    offset: int = 0
    limit: int = 100


@strawberry.type
class ListLabelApprovalJobsResponse:
    """Response from listing label approval jobs"""
    jobs: list[LabelApprovalJobDTO]
    total_count: int
    offset: int
    limit: int
    success: bool
    message: Optional[str] = None