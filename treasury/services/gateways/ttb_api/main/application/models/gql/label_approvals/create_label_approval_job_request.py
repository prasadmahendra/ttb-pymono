import uuid
from typing import Optional

import strawberry

from treasury.services.gateways.ttb_api.main.application.models.dto.label_approval_job_dto import LabelApprovalJobDTO


@strawberry.input
class JobMetadataInput:
    """Input for job metadata"""
    reviewer_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    review_comments: Optional[list[str]] = None
    alcohol_content_percentage: Optional[str] = None
    net_contents_in_milli_litres: Optional[str] = None
    bottler_info: Optional[str] = None
    manufacturer: Optional[str] = None
    warnings: Optional[str] = None
    label_image_base64: Optional[str] = None  # base64 representation of the label image


@strawberry.input
class CreateLabelApprovalJobInput:
    """Input for creating a new label approval job"""
    brand_name: uuid.UUID
    product_class: str
    status: Optional[str] = "pending"
    job_metadata: Optional[JobMetadataInput] = None


@strawberry.type
class CreateLabelApprovalJobResponse:
    """Response from creating a label approval job"""
    job: Optional[LabelApprovalJobDTO] = None
    success: bool
    message: Optional[str] = None