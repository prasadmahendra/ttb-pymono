"""DTOs for label image data"""

from datetime import datetime
from typing import Optional
import strawberry

from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import (
    LabelImage,
    LabelImageAnalysisResult
)
from treasury.services.gateways.ttb_api.main.application.models.dto.label_extraction_dto import BrandDataStrictDTO


@strawberry.experimental.pydantic.type(model=LabelImageAnalysisResult)
class LabelImageAnalysisResultDTO:
    """DTO for label image analysis result"""
    brand_name_found: bool = False
    brand_name_found_results_reasoning: Optional[str] = None
    product_class_found: bool = False
    product_class_found_results_reasoning: Optional[str] = None
    alcohol_content_found: bool = False
    alcohol_content_found_results_reasoning: Optional[str] = None
    net_contents_found: bool = False
    net_contents_found_results_reasoning: Optional[str] = None
    health_warning_found: Optional[bool] = None
    health_warning_found_results_reasoning: Optional[str] = None


@strawberry.experimental.pydantic.type(model=LabelImage)
class LabelImageDTO:
    """DTO for label image"""
    image_url: Optional[str] = None
    image_content_type: Optional[str] = None
    base64: Optional[str] = None
    upload_date: Optional[datetime] = None
    approved: Optional[bool] = None
    approved_date: Optional[datetime] = None
    rejected: Optional[bool] = None
    rejected_date: Optional[datetime] = None
    extracted_product_info: Optional[BrandDataStrictDTO] = None
    analysis_result: Optional[LabelImageAnalysisResultDTO] = None