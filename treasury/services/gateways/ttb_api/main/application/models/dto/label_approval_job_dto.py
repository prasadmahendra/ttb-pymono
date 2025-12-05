import uuid
from datetime import datetime
from typing import Optional

import strawberry

from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import JobMetadata, \
    LabelApprovalJob
from treasury.services.gateways.ttb_api.main.application.models.dto.label_extraction_dto import BrandDataStrictDTO
from treasury.services.gateways.ttb_api.main.application.models.dto.label_image_dto import LabelImageDTO


@strawberry.experimental.pydantic.type(model=JobMetadata)
class JobMetadataDTO:
    """DTO for job metadata"""
    reviewer_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    review_comments: Optional[list[str]] = None
    product_info: Optional[BrandDataStrictDTO] = None
    label_images: Optional[list[LabelImageDTO]] = None


@strawberry.experimental.pydantic.type(model=LabelApprovalJob)
class LabelApprovalJobDTO:
    """DTO for Label Approval Job"""
    id: uuid.UUID
    brand_name: uuid.UUID
    product_class: str
    status: str
    job_metadata: JobMetadataDTO
    created_at: datetime
    updated_at: datetime
    created_by_entity: str
    created_by_entity_id: str
    created_by_entity_domain: str
    updated_by_entity: str
    updated_by_entity_id: Optional[str] = None
    updated_by_entity_domain: Optional[str] = None