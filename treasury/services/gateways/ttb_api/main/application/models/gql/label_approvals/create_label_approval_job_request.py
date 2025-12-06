import uuid
from typing import Optional

import strawberry

from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import LabelApprovalStatus
from treasury.services.gateways.ttb_api.main.application.models.dto.label_approval_job_dto import LabelApprovalJobDTO


@strawberry.input
class JobMetadataInput:
    """Input for job metadata"""
    brand_name: Optional[str] = None
    product_class: Optional[str] = None
    alcohol_content_abv: Optional[str] = None
    net_contents: Optional[str] = None
    bottler_info: Optional[str] = None
    manufacturer: Optional[str] = None
    warnings: Optional[str] = None
    label_image_base64: Optional[str] = None  # base64 representation of the label image


@strawberry.input
class CreateLabelApprovalJobInput:
    """Input for creating a new label approval job"""
    status: Optional[LabelApprovalStatus] = LabelApprovalStatus.pending
    job_metadata: Optional[JobMetadataInput] = None


@strawberry.type
class CreateLabelApprovalJobResponse:
    """Response from creating a label approval job"""
    job: Optional[LabelApprovalJobDTO] = None
    success: bool
    message: Optional[str] = None