import uuid
from datetime import datetime
from typing import Optional

import strawberry

from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import JobMetadata, \
    LabelApprovalJob


@strawberry.experimental.pydantic.type(model=JobMetadata)
class JobMetadataDTO:
    """DTO for job metadata"""
    reviewer_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    review_comments: Optional[list[str]] = None
    alcohol_content: Optional[str] = None
    net_contents: Optional[str] = None
    bottler_info: Optional[str] = None
    manufacturer: Optional[str] = None
    warnings: Optional[str] = None


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