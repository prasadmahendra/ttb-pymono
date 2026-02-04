import json
import re
from typing import Optional

from treasury.services.gateways.ttb_api.main.adapter.out.llm.openai_adapter import OpenAiAdapter
from treasury.services.gateways.ttb_api.main.adapter.out.ocr.ocr_adapter import OcrAdapter
from treasury.services.gateways.ttb_api.main.application.config.config import GlobalConfig
from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import AnalysisMode
from treasury.services.gateways.ttb_api.main.application.models.domain.label_extraction_data import (
    BrandDataStrict,
    ProductInfoStrict,
    ProductOtherInfo
)
from treasury.services.gateways.ttb_api.main.application.usecases.llm_prompts import LlmPrompts


class LabelDataExtractionService:
    _logger = GlobalConfig.get_logger(__name__)

    def __init__(self, llm_client: OpenAiAdapter = None, ocr_adapter: OcrAdapter = None) -> None:
        self._llm_client_lazy = llm_client
        self._ocr_adapter_lazy = ocr_adapter

    @property
    def _llm_client(self) -> OpenAiAdapter:
        if self._llm_client_lazy is None:
            self._llm_client_lazy = OpenAiAdapter()
        return self._llm_client_lazy

    @property
    def _ocr_adapter(self) -> OcrAdapter:
        if self._ocr_adapter_lazy is None:
            self._ocr_adapter_lazy = OcrAdapter()
        return self._ocr_adapter_lazy

    def extract_label_data(
            self,
            base64_image: str,
            analysis_mode: AnalysisMode = AnalysisMode.using_llm
    ) -> BrandDataStrict:
        """
        Extract label data from image using either LLM or pytesseract based on analysis_mode.
        """
        if analysis_mode == AnalysisMode.pytesseract:
            return self._extract_label_data_with_pytesseract(base64_image)
        else:
            return self._extract_label_data_with_llm(base64_image)

    def _extract_label_data_with_llm(self, base64_image: str) -> BrandDataStrict:
        """Extract label data using LLM (OpenAI)"""
        llm_results: str = self._llm_client.complete_prompt_with_media(
            prompt=LlmPrompts.TTB_LABEL_IMAGE_INQUIRY_PROMPT,
            media_base64=base64_image,
        )
        self._logger.info(f"extract_label_data - LLM Results for base64_image: {llm_results}")

        # Parse JSON from LLM response (may include markdown code blocks)
        json_data = self.extract_json_from_response(llm_results)

        # Validate and parse into Pydantic model
        results = BrandDataStrict.model_validate(json_data)
        return results

    def _extract_label_data_with_pytesseract(self, base64_image: str) -> BrandDataStrict:
        """
        Extract label data using pytesseract OCR.
        Clips out substrings that match label field patterns.
        """
        ocr_result = self._ocr_adapter.extract_text(base64_encoded_image=base64_image)

        if not ocr_result.success:
            self._logger.warning(f"OCR extraction failed: {ocr_result.error_message}")
            return BrandDataStrict(brand_name=None, products=[])

        extracted_text = ocr_result.full_text
        self._logger.info(f"extract_label_data_pytesseract - OCR extracted text: {extracted_text[:500]}...")

        # Normalize text for pattern matching
        normalized_text = re.sub(r'\s+', ' ', extracted_text).strip()

        # Extract fields using regex patterns
        brand_name = self._extract_brand_name(normalized_text, extracted_text)
        alcohol_content = self._extract_alcohol_content(normalized_text)
        net_contents = self._extract_net_contents(normalized_text)
        product_class = self._extract_product_class(normalized_text)
        warnings = self._extract_warnings(extracted_text)  # Use original for GOVERNMENT WARNING check

        return BrandDataStrict(
            brand_name=brand_name,
            products=[
                ProductInfoStrict(
                    name=brand_name,
                    product_class_type=product_class,
                    alcohol_content_abv=alcohol_content,
                    net_contents=net_contents,
                    other_info=ProductOtherInfo(
                        bottler_info=None,
                        manufacturer=None,
                        warnings=warnings
                    )
                )
            ]
        )

    def _extract_brand_name(self, normalized_text: str, original_text: str) -> Optional[str]:
        """
        Extract brand name - typically the most prominent text on the label.
        Heuristic: Look for capitalized words or the first significant line.
        """
        # Try to find prominent capitalized text (potential brand name)
        # Look for sequences of capitalized words
        cap_words_pattern = r'\b([A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*)\b'
        matches = re.findall(cap_words_pattern, original_text)

        # Filter out common non-brand words
        ignore_words = {'GOVERNMENT', 'WARNING', 'CONTAINS', 'ALCOHOL', 'ABV', 'ALC', 'VOL', 'NET', 'CONTENTS'}

        for match in matches:
            words = match.split()
            # Skip if all words are in ignore list or too short
            if len(match) >= 3 and not all(w.upper() in ignore_words for w in words):
                self._logger.debug(f"Extracted brand name candidate: {match}")
                return match

        # Fallback: return first line that's not a warning
        lines = [line.strip() for line in original_text.split('\n') if line.strip()]
        for line in lines:
            if 'GOVERNMENT' not in line.upper() and 'WARNING' not in line.upper():
                if len(line) >= 3:
                    return line

        return None

    def _extract_alcohol_content(self, normalized_text: str) -> Optional[str]:
        """
        Extract alcohol content - look for patterns like "40%", "47.3% ABV", "ALC 40% BY VOL"
        """
        # Pattern: number followed by % (with optional decimal)
        patterns = [
            r'(\d+(?:\.\d+)?)\s*%\s*(?:abv|alc|alcohol|by\s*vol)',  # "40% ABV", "40% ALC BY VOL"
            r'(?:abv|alc|alcohol)\s*[:\.]?\s*(\d+(?:\.\d+)?)\s*%',  # "ABV: 40%", "ALC 40%"
            r'(\d+(?:\.\d+)?)\s*%\s*(?:vol|volume)',                 # "40% VOL"
            r'(\d+(?:\.\d+)?)\s*%',                                  # "40%" (generic)
        ]

        text_lower = normalized_text.lower()

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = match.group(1)
                result = f"{value}%"
                self._logger.debug(f"Extracted alcohol content: {result}")
                return result

        return None

    def _extract_net_contents(self, normalized_text: str) -> Optional[str]:
        """
        Extract net contents - look for volume patterns like "750 mL", "1L", "12 fl oz"
        """
        # Pattern: number followed by volume unit
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(ml|milliliters?|millilitres?)',     # "750 mL"
            r'(\d+(?:\.\d+)?)\s*(cl|centiliters?|centilitres?)',     # "70 cL"
            r'(\d+(?:\.\d+)?)\s*(l|liters?|litres?)',                # "1 L" or "1 liter"
            r'(\d+(?:\.\d+)?)\s*(fl\.?\s*oz\.?|fluid\s*ounces?)',    # "12 fl oz"
            r'(\d+(?:\.\d+)?)\s*(oz\.?|ounces?)',                    # "12 oz"
            r'(\d+(?:\.\d+)?)\s*(gal\.?|gallons?)',                  # "1 gal"
        ]

        text_lower = normalized_text.lower()

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = match.group(1)
                unit = match.group(2)
                # Normalize unit
                unit_map = {
                    'ml': 'mL', 'milliliter': 'mL', 'millilitre': 'mL',
                    'milliliters': 'mL', 'millilitres': 'mL',
                    'cl': 'cL', 'centiliter': 'cL', 'centilitre': 'cL',
                    'centiliters': 'cL', 'centilitres': 'cL',
                    'l': 'L', 'liter': 'L', 'litre': 'L', 'liters': 'L', 'litres': 'L',
                    'fl oz': 'fl oz', 'fl. oz': 'fl oz', 'fl. oz.': 'fl oz',
                    'fluid ounce': 'fl oz', 'fluid ounces': 'fl oz',
                    'oz': 'oz', 'oz.': 'oz', 'ounce': 'oz', 'ounces': 'oz',
                    'gal': 'gal', 'gal.': 'gal', 'gallon': 'gal', 'gallons': 'gal',
                }
                normalized_unit = unit_map.get(unit.lower().strip(), unit)
                result = f"{value} {normalized_unit}"
                self._logger.debug(f"Extracted net contents: {result}")
                return result

        return None

    def _extract_product_class(self, normalized_text: str) -> Optional[str]:
        """
        Extract product class/type - look for common alcohol type keywords
        """
        # Common product classes (order matters - more specific first)
        product_classes = [
            ('kentucky straight bourbon whiskey', 'Kentucky Straight Bourbon Whiskey'),
            ('straight bourbon whiskey', 'Straight Bourbon Whiskey'),
            ('bourbon whiskey', 'Bourbon Whiskey'),
            ('tennessee whiskey', 'Tennessee Whiskey'),
            ('scotch whisky', 'Scotch Whisky'),
            ('single malt', 'Single Malt Whisky'),
            ('rye whiskey', 'Rye Whiskey'),
            ('irish whiskey', 'Irish Whiskey'),
            ('canadian whisky', 'Canadian Whisky'),
            ('whiskey', 'Whiskey'),
            ('whisky', 'Whisky'),
            ('bourbon', 'Bourbon'),
            ('london dry gin', 'London Dry Gin'),
            ('dry gin', 'Dry Gin'),
            ('gin', 'Gin'),
            ('vodka', 'Vodka'),
            ('white rum', 'White Rum'),
            ('dark rum', 'Dark Rum'),
            ('spiced rum', 'Spiced Rum'),
            ('rum', 'Rum'),
            ('reposado tequila', 'Reposado Tequila'),
            ('anejo tequila', 'Anejo Tequila'),
            ('blanco tequila', 'Blanco Tequila'),
            ('tequila', 'Tequila'),
            ('mezcal', 'Mezcal'),
            ('cognac', 'Cognac'),
            ('brandy', 'Brandy'),
            ('lager beer', 'Lager Beer'),
            ('pale ale', 'Pale Ale'),
            ('india pale ale', 'India Pale Ale'),
            ('ipa', 'IPA'),
            ('stout', 'Stout'),
            ('porter', 'Porter'),
            ('pilsner', 'Pilsner'),
            ('lager', 'Lager'),
            ('ale', 'Ale'),
            ('beer', 'Beer'),
            ('red wine', 'Red Wine'),
            ('white wine', 'White Wine'),
            ('rose wine', 'Rose Wine'),
            ('sparkling wine', 'Sparkling Wine'),
            ('champagne', 'Champagne'),
            ('wine', 'Wine'),
        ]

        text_lower = normalized_text.lower()

        for pattern, label in product_classes:
            if pattern in text_lower:
                self._logger.debug(f"Extracted product class: {label}")
                return label

        return None

    def _extract_warnings(self, original_text: str) -> Optional[str]:
        """
        Extract health/government warning text
        """
        if 'GOVERNMENT WARNING' in original_text:
            # Try to extract the full warning text
            warning_pattern = r'GOVERNMENT WARNING[:\s]*(.+?)(?:\n\n|\Z)'
            match = re.search(warning_pattern, original_text, re.DOTALL | re.IGNORECASE)
            if match:
                warning_text = f"GOVERNMENT WARNING: {match.group(1).strip()}"
                self._logger.debug(f"Extracted warning: {warning_text[:100]}...")
                return warning_text
            return "GOVERNMENT WARNING"
        return None

    @classmethod
    def extract_json_from_response(cls, response: str) -> dict:
        """
        Extract JSON from LLM response, handling markdown code blocks
        Args:
            response: Raw LLM response string
        Returns:
            Parsed JSON as dictionary
        Raises:
            ValueError: If JSON cannot be extracted or parsed
        """
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Assume entire response is JSON
                json_str = response

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            cls._logger.error(f"Failed to parse JSON from LLM response: {str(e)}")
            cls._logger.error(f"Response: {response}")
            raise ValueError(f"Could not parse JSON from LLM response: {str(e)}")

