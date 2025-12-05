class LlmPrompts:
    _TTB_LABEL_EXTRACTION_SCHEMA = """
export type ABV = `${number}%`;
export type Volume = `${number} mL` | `${number} cL` | `${number} fl oz`;

export interface ProductInfoStrict {
  name: string;
  product_class_type: string; // The general class or type of the beverage. For distilled spirits this could be the class/type designation (e.g. Kentucky Straight Bourbon Whiskey or Vodka), for beer it might be style (e.g. IPA), etc.
  alcohol_content_abv: ABV;
  net_contents: Volume;
  other_info: {
    bottler_info: string;
    manufacturer: string;
    warnings: string;
  };
}

export interface BrandDataStrict {
  brand_name: string; // The brand under which the product is sold (e.g. Old Tom Distillery).
  products: ProductInfoStrict[];
}    
    """

    TTB_LABEL_IMAGE_INQUIRY_PROMPT = f"""
You are an expert in extracting structured data from product label images for regulatory compliance.
Given an image of a product label, your task is to extract key information and format it according
to the following TypeScript interfaces:
{_TTB_LABEL_EXTRACTION_SCHEMA}
Analyze the label image carefully and populate the fields in the interfaces as accurately as possible.
If certain information is missing or unclear on the label, use "Unknown" for string fields and
"0%" or "0 mL" for ABV and Volume fields respectively.

Return only the exact text found on the label for each field, without any additional commentary or explanation.
Do not include any fields that are not specified in the interfaces. 
Do not add any extra formatting, markdown, or code blocks.
Do not convert units; use the units as they appear on the label.

Provide the final output as a JSON object that adheres strictly to the BrandDataStrict interface.
"""