from treasury.services.gateways.ttb_api.main.application.models.domain.label_extraction_data import BrandDataStrict


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
Alcohol and Tobacco Tax and Trade Bureau. 
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

    _TTB_LABEL_ANALYSIS_SCHEMA = """
    export interface LabelImageAnalysisResult {
// Does the text on the label contain the Brand Name exactly as provided?
brand_name_found: boolean;
brand_name_found_results_reasoning?: string | null;

// Does it contain the stated Product Class/Type?
product_class_found: boolean;
product_class_found_results_reasoning?: string | null;

// Does it mention the Alcohol Content (look for number + "%")?
alcohol_content_found: boolean;
alcohol_content_found_results_reasoning?: string | null;

// Does the Net Contents (e.g. "750 mL") appear?
net_contents_found: boolean;
net_contents_found_results_reasoning?: string | null;

// Does the label include a health/government warning?
health_warning_found: boolean;
health_warning_found_results_reasoning?: string | null;
}
"""

    @classmethod
    def get_label_analysis_prompt(cls, given_brand_label_info: BrandDataStrict, extracted_brand_label_info: BrandDataStrict) -> str:
        prompt = f"""
You are an expert in regulatory compliance for alcoholic beverage labels at the Alcohol and Tobacco Tax and Trade Bureau. 
A merchant has submitted a product label for approval. You have the following information provided by the merchant about the product:
{given_brand_label_info.model_dump_json(indent=2)}

You have also extracted the following information from the submitted product label image:
{extracted_brand_label_info.model_dump_json(indent=2)}
        
Analyze the extracted label data against the merchant-provided information and answer the following questions, the answers should be either True or False, along with a brief reasoning for each.
        The schema for the extracted data is as follows:
{cls._TTB_LABEL_ANALYSIS_SCHEMA}
        
1. Does the text on the label contain the Brand Name exactly as provided in the form?
2. Does it contain the stated Product Class/Type (or something very close/identical
3. Does it mention the Alcohol Content (within the text, look for a number and “%” that matches the form input)?
4. If you included Net Contents in the form, check if the volume (e.g. “750 mL” or “12 OZ”) appears on the label.
5. Health Warning Statement: For alcoholic beverages, a government warning is mandatory by law. Check that the phrase “GOVERNMENT WARNING” appears on the label image text.

Provide the final output as a JSON object that adheres strictly to the LabelImageAnalysisResult interface.
        """
        return prompt