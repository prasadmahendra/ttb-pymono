import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Union

from sqlalchemy import Column, JSON
from sqlalchemy.sql.schema import Index
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, field_validator, field_serializer

class LabelApprovalStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class LabelImage(BaseModel):
    image_url: Optional[str] = None
    image_content_type: Optional[str] = None

    # For the purpose of this coding test, we include base64 representation of the image
    # and keep these in our memory based SQL model.
    # In a real-world scenario, this will not be practical for large images, and at scale,
    # we would store images in a dedicated object storage service (e.g., AWS S3) and only
    # keep the URL/reference here.
    base64: Optional[str] = None
    upload_date: Optional[datetime] = None
    approved: Optional[bool] = None
    approved_date: Optional[datetime] = None
    rejected: Optional[bool] = None
    rejected_date: Optional[datetime] = None

class JobMetadata(BaseModel):
    reviewer_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    review_comments: Optional[list[str]] = None
    alcohol_content_percentage: Optional[str] = None
    net_contents_in_milli_litres: Optional[str] = None

    # Bonus fields (optional for the coding test)
    bottler_info: Optional[str] = None
    manufacturer: Optional[str] = None
    warnings: Optional[str] = None
    label_images: Optional[list[LabelImage]] = None


def _serialize_job_metadata(v: JobMetadata) -> dict[str, Any]:
    """Serialize JobMetadata to dict for database storage"""
    return v.model_dump(exclude_none=False)


def _validate_job_metadata(v: Union[dict, JobMetadata]) -> JobMetadata:
    """Deserialize dict to JobMetadata when loading from database"""
    if isinstance(v, dict):
        return JobMetadata(**v)
    return v


class LabelApprovalJob(SQLModel, table=True):
    __tablename__ = "label_approval_jobs"
    __table_args__ = (
        Index("status_idx", "status", "created_at"),
    )

    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    brand_name: Optional[str] = Field(nullable=False)
    product_class: Optional[str] = Field(nullable=False)
    status: str = Field(default=LabelApprovalStatus.pending.value, nullable=False)
    job_metadata: dict[str, Any] = Field(sa_column=Column("metadata", JSON, nullable=False), default_factory=lambda: JobMetadata().model_dump(exclude_none=False))
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)
    created_by_entity: str = Field(nullable=False)
    created_by_entity_id: str = Field(nullable=False)
    created_by_entity_domain: str = Field(nullable=False)
    updated_by_entity: str = Field(nullable=False)
    updated_by_entity_id: Optional[str] = Field(default=None, nullable=True)
    updated_by_entity_domain: Optional[str] = Field(default=None, nullable=True)

    @field_validator('job_metadata', mode='before')
    @classmethod
    def validate_job_metadata(cls, v: Union[dict, JobMetadata]) -> dict[str, Any]:
        """Convert JobMetadata to dict before assignment"""
        if isinstance(v, JobMetadata):
            return v.model_dump(exclude_none=False)
        return v

    @field_serializer('job_metadata')
    def serialize_job_metadata(self, v: Union[dict, JobMetadata], _info) -> dict[str, Any]:
        """Serialize job_metadata to dict"""
        if isinstance(v, JobMetadata):
            return v.model_dump(exclude_none=False)
        return v

    def get_job_metadata(self) -> JobMetadata:
        """Get job metadata as JobMetadata object"""
        return JobMetadata.model_validate(self.job_metadata)
