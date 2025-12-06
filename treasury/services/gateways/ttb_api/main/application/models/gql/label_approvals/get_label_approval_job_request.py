import uuid
from typing import Optional

import strawberry

from treasury.services.gateways.ttb_api.main.application.models.dto.label_approval_job_dto import LabelApprovalJobDTO


@strawberry.input
class GetLabelApprovalJobInput:
    """Input for getting a single label approval job by ID"""
    job_id: uuid.UUID


@strawberry.type
class GetLabelApprovalJobResponse:
    """Response from getting a label approval job"""
    job: Optional[LabelApprovalJobDTO] = None
    success: bool
    message: Optional[str] = None