import uuid
from typing import Optional

import strawberry

from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import AnalysisMode
from treasury.services.gateways.ttb_api.main.application.models.dto import LabelApprovalJobDTO


@strawberry.input
class AnalyzeLabelApprovalJobInput:
    """Input for analyzing a label approval job"""
    job_id: uuid.UUID
    analysis_mode: Optional[AnalysisMode] = None  # Optional override for ad-hoc runs (not persisted)

@strawberry.type
class AnalyzeLabelApprovalJobResponse:
    """Response from creating a label approval job"""
    job: Optional[LabelApprovalJobDTO] = None
    success: bool
    message: Optional[str] = None