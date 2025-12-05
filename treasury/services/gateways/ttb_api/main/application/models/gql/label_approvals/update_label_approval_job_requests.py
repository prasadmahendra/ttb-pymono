import uuid
from typing import Optional

import strawberry

from treasury.services.gateways.ttb_api.main.application.models.dto.label_approval_job_dto import LabelApprovalJobDTO


@strawberry.input
class SetLabelApprovalJobStatusInput:
    """Input for setting label approval job status"""
    job_id: uuid.UUID
    status: str
    review_comment: Optional[str] = None


@strawberry.type
class SetLabelApprovalJobStatusResponse:
    """Response from setting label approval job status"""
    job: Optional[LabelApprovalJobDTO] = None
    success: bool
    message: Optional[str] = None


@strawberry.input
class AddReviewCommentInput:
    """Input for adding a review comment to a label approval job"""
    job_id: uuid.UUID
    review_comment: str


@strawberry.type
class AddReviewCommentResponse:
    """Response from adding a review comment"""
    job: Optional[LabelApprovalJobDTO] = None
    success: bool
    message: Optional[str] = None