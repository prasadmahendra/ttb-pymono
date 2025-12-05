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
    bottler_info: strawberry.auto
    manufacturer: strawberry.auto
    warnings: strawberry.auto


@strawberry.experimental.pydantic.type(model=ProductInfoStrict)
class ProductInfoStrictDTO:
    """DTO for product info"""
    name: strawberry.auto
    product_class_type: strawberry.auto
    alcohol_content_abv: strawberry.auto
    net_contents: strawberry.auto
    other_info: Optional[ProductOtherInfoDTO] = None


@strawberry.experimental.pydantic.type(model=BrandDataStrict)
class BrandDataStrictDTO:
    """DTO for brand data"""
    brand_name: strawberry.auto
    products: list[ProductInfoStrictDTO] = strawberry.field(default_factory=list)