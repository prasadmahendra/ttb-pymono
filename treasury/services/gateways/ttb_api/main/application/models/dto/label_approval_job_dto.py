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
    reviewer_id: strawberry.auto
    reviewer_name: strawberry.auto
    review_comments: strawberry.auto
    product_info: Optional[BrandDataStrictDTO]
    label_images: Optional[list[LabelImageDTO]]


@strawberry.experimental.pydantic.type(model=LabelApprovalJob)
class LabelApprovalJobDTO:
    """DTO for Label Approval Job"""
    id: uuid.UUID
    brand_name: str
    product_class: strawberry.auto
    status: strawberry.auto
    job_metadata: JobMetadataDTO
    created_at: strawberry.auto
    updated_at: strawberry.auto
    created_by_entity: strawberry.auto
    created_by_entity_id: strawberry.auto
    created_by_entity_domain: strawberry.auto
    updated_by_entity: strawberry.auto
    updated_by_entity_id: strawberry.auto
    updated_by_entity_domain: strawberry.auto