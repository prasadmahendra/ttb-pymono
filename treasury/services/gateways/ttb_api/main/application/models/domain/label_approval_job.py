import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Union

from sqlalchemy import Column, JSON
from sqlalchemy.sql.schema import Index
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, field_validator, field_serializer, model_validator

from treasury.services.gateways.ttb_api.main.application.models.domain.label_extraction_data import ProductOtherInfo, \
    ProductInfoStrict, BrandDataStrict


class LabelApprovalStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class AnalysisMode(str, Enum):
    using_llm = "using_llm"
    pytesseract = "pytesseract"


class LabelImageAnalysisResult(BaseModel):
    # Does the text on the label contain the Brand Name exactly as provided in the form?
    brand_name_found: bool = False
    brand_name_found_results_reasoning: Optional[str] = None

    # Does it contain the stated Product Class/Type (or something very close/identical)?
    product_class_found: bool = False
    product_class_found_results_reasoning: Optional[str] = None

    # Does it mention the Alcohol Content (within the text, look for a number and “%” that matches the
    # form input)?
    alcohol_content_found: bool = False
    alcohol_content_found_results_reasoning: Optional[str] = None

    # If you included Net Contents in the form, check if the volume (e.g. “750 mL” or “12 OZ”) appears on
    # the label.
    net_contents_found: bool = False
    net_contents_found_results_reasoning: Optional[str] = None

    # Health Warning Statement: For alcoholic beverages, a government warning is mandatory by law. A
    # real TTB check would verify that the label has the exact text of the warning statement (the
    # standardized text about pregnancy and driving) . For simplicity, you can at least check that the
    # phrase “GOVERNMENT WARNING” appears on the label image text (and possibly that some portion
    # of the warning text is present). This can be a bonus feature if you have time.
    health_warning_found: Optional[bool] = None
    health_warning_found_results_reasoning: Optional[str] = None


class LabelImage(BaseModel):
    # New records: image uploaded to Vercel Blob Storage, image_url is set, base64 is None.
    # Old records: base64 is set, image_url is None — analysis services check both.
    image_url: Optional[str] = None
    image_content_type: Optional[str] = None

    # Kept for backward compatibility with old records that stored base64 directly.
    # New records will have base64=None and image_url set instead.
    base64: Optional[str] = None
    upload_date: Optional[datetime] = None
    approved: Optional[bool] = None
    approved_date: Optional[datetime] = None
    rejected: Optional[bool] = None
    rejected_date: Optional[datetime] = None

    extracted_product_info: Optional[BrandDataStrict] = None
    analysis_result: Optional[LabelImageAnalysisResult] = None


class JobMetadata(BaseModel):
    reviewer_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    review_comments: Optional[list[str]] = None
    product_info: Optional[BrandDataStrict] = None
    label_images: Optional[list[LabelImage]] = None
    analysis_mode: Optional[AnalysisMode] = AnalysisMode.using_llm


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
    status: LabelApprovalStatus = Field(default=LabelApprovalStatus.pending, nullable=False)
    job_metadata: Union[dict, JobMetadata] = Field(
        sa_column=Column("metadata", JSON, nullable=False),
        default_factory=lambda: JobMetadata().model_dump(exclude_none=True),
    )
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
    def validate_job_metadata(cls, v: Union[dict, JobMetadata]) -> Union[dict, JobMetadata]:
        """Convert dict to JobMetadata before assignment"""
        if isinstance(v, dict):
            return JobMetadata(**v)
        return v

    @field_serializer('job_metadata')
    def serialize_job_metadata(self, v: Union[dict, JobMetadata], _info) -> dict[str, Any]:
        """Serialize job_metadata to dict"""
        if isinstance(v, JobMetadata):
            return v.model_dump(exclude_none=False)
        return v

    def get_job_metadata(self) -> JobMetadata:
        """Get job metadata as JobMetadata object"""
        return self.job_metadata
