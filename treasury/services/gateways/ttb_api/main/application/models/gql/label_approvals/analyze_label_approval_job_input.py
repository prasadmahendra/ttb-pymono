import uuid
from typing import Optional

import strawberry

from treasury.services.gateways.ttb_api.main.application.models.dto import LabelApprovalJobDTO


@strawberry.input
class AnalyzeLabelApprovalJobInput:
    """Input for analyzing a label approval job"""
    job_id: uuid.UUID

@strawberry.type
class AnalyzeLabelApprovalJobResponse:
    """Response from creating a label approval job"""
    job: Optional[LabelApprovalJobDTO] = None
    success: bool
    message: Optional[str] = None