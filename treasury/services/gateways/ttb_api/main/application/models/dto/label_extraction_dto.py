"""DTOs for label extraction data"""

from typing import Optional
import strawberry

from treasury.services.gateways.ttb_api.main.application.models.domain.label_extraction_data import (
    ProductOtherInfo,
    ProductInfoStrict,
    BrandDataStrict
)


@strawberry.experimental.pydantic.type(model=ProductOtherInfo)
class ProductOtherInfoDTO:
    """DTO for product other info"""
    bottler_info: Optional[str] = None
    manufacturer: Optional[str] = None
    warnings: Optional[str] = None


@strawberry.experimental.pydantic.type(model=ProductInfoStrict)
class ProductInfoStrictDTO:
    """DTO for product info"""
    name: Optional[str] = None
    product_class_type: Optional[str] = None
    alcohol_content_abv: Optional[str] = None
    net_contents: Optional[str] = None
    other_info: Optional[ProductOtherInfoDTO] = None


@strawberry.experimental.pydantic.type(model=BrandDataStrict)
class BrandDataStrictDTO:
    """DTO for brand data"""
    brand_name: Optional[str] = None
    products: list[ProductInfoStrictDTO] = strawberry.field(default_factory=list)