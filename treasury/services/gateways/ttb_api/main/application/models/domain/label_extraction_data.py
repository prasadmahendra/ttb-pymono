from pydantic import BaseModel, Field
from typing import List, Optional
import re


class ProductOtherInfo(BaseModel):
    bottler_info: Optional[str] = None
    manufacturer: Optional[str] = None
    warnings: Optional[str] = None


class ProductInfoStrict(BaseModel):
    name: Optional[str] = None
    product_class_type: Optional[str] = None

    # Matches "41%" or "41.3%"
    alcohol_content_abv: Optional[str] = Field(
        default=None,
        pattern=r"^\d+(\.\d+)?%$",
        description="Alcohol by volume, e.g. '41%' or '41.3%'"
    )

    # Matches “700 mL”, “70 cL”, “12 fl oz”
    net_contents: Optional[str] = Field(
        default=None,
        pattern=r"^\d+(\.\d+)?\s?(mL|cL|fl oz)$",
        description="Net contents with unit, e.g. '700 mL'"
    )

    other_info: Optional[ProductOtherInfo] = None

    def alcohol_content_abv_cleaned(self) -> float:
        """Convert alcohol content to float percentage"""
        match = re.match(r"^(\d+(\.\d+)?)%$", self.alcohol_content_abv)
        if not match:
            raise ValueError(f"Invalid alcohol content format: {self.alcohol_content_abv}")
        return float(match.group(1))

    def net_contents_as_millilitres(self) -> float:
        """Convert net contents to millilitres"""
        match = re.match(r"^(\d+(\.\d+)?)\s?(mL|cL|fl oz)$", self.net_contents)
        if not match:
            raise ValueError(f"Invalid net contents format: {self.net_contents}")

        quantity = float(match.group(1))
        unit = match.group(3)

        if unit == "mL":
            return quantity
        elif unit == "cL":
            return quantity * 10
        elif unit == "fl oz":
            return quantity * 29.5735  # 1 fl oz = 29.5735 mL
        else:
            raise ValueError(f"Unknown unit: {unit}")


class BrandDataStrict(BaseModel):
    brand_name: Optional[str] = None
    products: List[ProductInfoStrict] = []
