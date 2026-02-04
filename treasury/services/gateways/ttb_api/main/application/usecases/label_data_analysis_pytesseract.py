"""Label data analysis using pytesseract OCR"""
from typing import Optional

from treasury.services.gateways.ttb_api.main.adapter.out.ocr.ocr_adapter import OcrAdapter
from treasury.services.gateways.ttb_api.main.adapter.out.ocr.ocr_models import OcrResult
from treasury.services.gateways.ttb_api.main.application.config.config import GlobalConfig
from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import (
    LabelApprovalJob,
    LabelImageAnalysisResult,
    LabelImage,
    JobMetadata
)
from treasury.services.gateways.ttb_api.main.application.models.domain.label_extraction_data import BrandDataStrict


class LabelDataAnalysisPytesseractService:
    """Service for analyzing label data using pytesseract OCR"""

    def __init__(self, ocr_adapter: OcrAdapter = None) -> None:
        self._ocr_adapter_lazy = ocr_adapter
        self._logger = GlobalConfig.get_logger(__name__)

    @property
    def _ocr_adapter(self) -> OcrAdapter:
        if self._ocr_adapter_lazy is None:
            self._ocr_adapter_lazy = OcrAdapter()
        return self._ocr_adapter_lazy

    def answer_analysis_questions_with_pytesseract(
            self,
            job: LabelApprovalJob,
            image_to_analyze: LabelImage
    ) -> Optional[LabelApprovalJob]:
        """Analyze the extracted label data and answer the analysis questions using pytesseract OCR"""

        given_brand_label_info = job.get_job_metadata().product_info

        try:
            # Extract text from image using pytesseract
            ocr_result: OcrResult = self._ocr_adapter.extract_text(
                base64_encoded_image=image_to_analyze.base64
            )

            if not ocr_result.success:
                self._logger.warning(f"OCR extraction failed for job={job.id}: {ocr_result.error_message}")
                return None

            extracted_text = ocr_result.full_text
            self._logger.info(f"OCR extracted text for job={job.id}: {extracted_text[:500]}...")

            # Analyze the extracted text against given brand info
            analysis_result = self._analyze_ocr_text(
                extracted_text=extracted_text,
                given_brand_info=given_brand_label_info
            )

            # Clone and update job
            job_clone = LabelApprovalJob.model_validate(job.model_dump())
            job_metadata_clone: JobMetadata = job_clone.get_job_metadata()

            image_to_analyze_clone: LabelImage = image_to_analyze.model_copy(deep=True)
            image_to_analyze_clone.analysis_result = analysis_result

            # Replace the first image with the updated one
            job_metadata_clone.label_images[0] = image_to_analyze_clone
            job_clone.job_metadata = job_metadata_clone

            return job_clone

        except Exception as e:
            self._logger.exception(f"answer_analysis_questions_with_pytesseract - Error during label analysis job={job.id} error={e}")
            return None

    def _analyze_ocr_text(
            self,
            extracted_text: str,
            given_brand_info: Optional[BrandDataStrict]
    ) -> LabelImageAnalysisResult:
        """
        Analyze OCR extracted text against given brand information.

        Case sensitivity rules:
        1. Brand Name - case-INSENSITIVE (e.g., "STONE'S THROW" matches "Stone's Throw")
        2. Product Class/Type - case-INSENSITIVE, with fuzzy matching for related types
        3. Alcohol Content - case-INSENSITIVE, number + "%" match
        4. Net Contents - case-INSENSITIVE, volume match (e.g., "750 mL", "12 OZ")
        5. Health Warning - ONLY field requiring ALL CAPS ("GOVERNMENT WARNING" exact match)
        """
        result = LabelImageAnalysisResult()
        extracted_text_lower = extracted_text.lower()

        if not given_brand_info:
            return result

        # 1. Check brand name - case-insensitive match (e.g., "STONE'S THROW" matches "Stone's Throw")
        if given_brand_info.brand_name:
            brand_name_lower = given_brand_info.brand_name.lower()
            brand_name_found = brand_name_lower in extracted_text_lower
            result.brand_name_found = brand_name_found
            if brand_name_found:
                result.brand_name_found_results_reasoning = (
                    f"The brand name '{given_brand_info.brand_name}' was found on the label (case-insensitive match) using OCR text extraction."
                )
            else:
                result.brand_name_found_results_reasoning = (
                    f"The form specifies a brand name of '{given_brand_info.brand_name}', but the OCR extracted label data "
                    f"does not contain this text (case-insensitive search), indicating the brand name was not found on the label."
                )

        # Check product info from first product
        if given_brand_info.products and len(given_brand_info.products) > 0:
            product = given_brand_info.products[0]

            # 2. Check product class/type - allow close matches
            if product.product_class_type:
                product_class_lower = product.product_class_type.lower()
                # Check for exact match or common variations
                product_class_found = self._check_product_class_match(product_class_lower, extracted_text_lower)
                result.product_class_found = product_class_found
                if product_class_found:
                    result.product_class_found_results_reasoning = (
                        f"The product class '{product.product_class_type}' (or a close equivalent) was found on the label using OCR text extraction."
                    )
                else:
                    result.product_class_found_results_reasoning = (
                        f"The form specifies a product class of '{product.product_class_type}', but the OCR extracted label data "
                        f"does not contain this text or a close equivalent, indicating the product class was not found on the label."
                    )

            # 3. Check alcohol content - look for number + "%"
            if product.alcohol_content_abv:
                alcohol_value = product.alcohol_content_abv.replace('%', '').strip()
                self._logger.debug(f"Checking alcohol content: looking for '{alcohol_value}' in extracted text")
                alcohol_found = self._check_alcohol_content_match(alcohol_value, extracted_text_lower)
                result.alcohol_content_found = alcohol_found
                self._logger.debug(f"Alcohol content match result: {alcohol_found}")
                if alcohol_found:
                    result.alcohol_content_found_results_reasoning = (
                        f"The alcohol content '{product.alcohol_content_abv}' was found on the label using OCR text extraction."
                    )
                else:
                    result.alcohol_content_found_results_reasoning = (
                        f"The form specifies an alcohol content of '{product.alcohol_content_abv}', but the OCR extracted label data "
                        f"does not show this value, indicating no matching alcohol percentage was found on the label."
                    )

            # 4. Check net contents - volume match
            if product.net_contents:
                self._logger.debug(f"Checking net contents: looking for '{product.net_contents}' in extracted text")
                net_contents_found = self._check_net_contents_match(product.net_contents, extracted_text_lower)
                result.net_contents_found = net_contents_found
                self._logger.debug(f"Net contents match result: {net_contents_found}")
                if net_contents_found:
                    result.net_contents_found_results_reasoning = (
                        f"The net contents '{product.net_contents}' was found on the label using OCR text extraction."
                    )
                else:
                    result.net_contents_found_results_reasoning = (
                        f"The form specifies net contents of '{product.net_contents}', but the OCR extracted label data "
                        f"does not show this value, indicating the net contents was not found on the label."
                    )

            # 5. Check health warning - "GOVERNMENT WARNING" must be ALL CAPS
            warnings_were_given = (
                product.other_info is not None and
                product.other_info.warnings is not None and
                len(product.other_info.warnings.strip()) > 0
            )

            if warnings_were_given:
                # Check for exact "GOVERNMENT WARNING" in ALL CAPS in original text (not lowercased)
                health_warning_found = "GOVERNMENT WARNING" in extracted_text
                result.health_warning_found = health_warning_found
                if health_warning_found:
                    result.health_warning_found_results_reasoning = (
                        "The required 'GOVERNMENT WARNING' text was found on the label in the correct all-caps format using OCR text extraction."
                    )
                else:
                    result.health_warning_found_results_reasoning = (
                        "The form requires a government warning, but the OCR extracted label data does not contain "
                        "'GOVERNMENT WARNING' in the required all-caps format."
                    )
            else:
                result.health_warning_found = None
                result.health_warning_found_results_reasoning = "Not applicable - no warnings provided in the form."

        return result

    def _check_product_class_match(self, given_class: str, extracted_text: str) -> bool:
        """
        Check for product class match, allowing close equivalents.
        E.g., Beer and Lager Beer are the same, Gin and London Gin are the same.
        """
        # Direct match
        if given_class in extracted_text:
            return True

        # Common equivalents mapping
        equivalents = {
            'beer': ['lager beer', 'lager', 'ale', 'pilsner'],
            'lager beer': ['beer', 'lager', 'pilsner'],
            'gin': ['london gin', 'london dry gin', 'dry gin'],
            'london gin': ['gin', 'london dry gin', 'dry gin'],
            'vodka': ['vodka'],
            'whiskey': ['whisky', 'bourbon', 'rye whiskey', 'scotch'],
            'whisky': ['whiskey', 'bourbon', 'rye whisky', 'scotch'],
            'bourbon': ['whiskey', 'whisky', 'kentucky bourbon', 'straight bourbon'],
            'rum': ['rum', 'dark rum', 'white rum', 'gold rum'],
            'tequila': ['tequila', 'mezcal'],
            'wine': ['wine', 'red wine', 'white wine', 'rose wine'],
        }

        # Check if given class has equivalents and any match
        if given_class in equivalents:
            for equivalent in equivalents[given_class]:
                if equivalent in extracted_text:
                    return True

        # Check if extracted text contains the base category
        for base_class, variants in equivalents.items():
            if given_class in variants and base_class in extracted_text:
                return True

        return False

    def _check_alcohol_content_match(self, alcohol_value: str, extracted_text: str) -> bool:
        """
        Check for alcohol content match - look for number + "%" patterns.
        OCR text may have newlines, extra whitespace, so normalize before matching.
        """
        import re

        # Normalize extracted text: replace newlines and multiple spaces with single space
        normalized_text = re.sub(r'\s+', ' ', extracted_text).strip()

        # Various patterns to match
        patterns_to_check = [
            f"{alcohol_value}%",           # "47.3%"
            f"{alcohol_value} %",          # "47.3 %"
            f"{alcohol_value}% alc",       # "47.3% alc"
            f"{alcohol_value}% abv",       # "47.3% abv"
            f"alc {alcohol_value}%",       # "alc 47.3%"
            f"abv {alcohol_value}%",       # "abv 47.3%"
            f"{alcohol_value} % alc",      # "47.3 % alc"
            f"{alcohol_value} % abv",      # "47.3 % abv"
            f"alcohol {alcohol_value}%",   # "alcohol 47.3%"
        ]

        for pattern in patterns_to_check:
            if pattern in normalized_text:
                return True

        # Also try regex pattern for more flexible matching (handles spacing variations)
        # Match: number, optional space, %, anywhere in text
        regex_pattern = rf'{re.escape(alcohol_value)}\s*%'
        if re.search(regex_pattern, normalized_text):
            return True

        return False

    def _check_net_contents_match(self, net_contents: str, extracted_text: str) -> bool:
        """
        Check for net contents match - volume patterns like "750 mL", "12 OZ".
        OCR text may have newlines, extra whitespace, so normalize before matching.
        """
        import re

        # Normalize extracted text: replace newlines and multiple spaces with single space
        normalized_text = re.sub(r'\s+', ' ', extracted_text).strip()

        net_contents_lower = net_contents.lower()

        # Direct match
        if net_contents_lower in normalized_text:
            return True

        # Without spaces (e.g., "750ml" vs "750 ml")
        net_contents_no_space = net_contents_lower.replace(' ', '')
        normalized_no_space = normalized_text.replace(' ', '')
        if net_contents_no_space in normalized_no_space:
            return True

        # Common unit variations
        unit_variations = {
            'ml': ['ml', 'milliliter', 'millilitre', 'milliliters', 'millilitres'],
            'cl': ['cl', 'centiliter', 'centilitre', 'centiliters', 'centilitres'],
            'fl oz': ['fl oz', 'fl. oz.', 'fl. oz', 'fluid ounce', 'fluid ounces', 'floz'],
            'oz': ['oz', 'oz.', 'ounce', 'ounces'],
            'l': ['l', 'liter', 'litre', 'liters', 'litres'],
            'gal': ['gal', 'gal.', 'gallon', 'gallons'],
        }

        # Extract numeric value and unit from given net contents
        match = re.match(r'(\d+(?:\.\d+)?)\s*(.+)', net_contents_lower)
        if match:
            value = match.group(1)
            unit = match.group(2).strip()

            # Find the base unit
            base_unit = None
            for base, variations in unit_variations.items():
                if unit in variations or unit == base:
                    base_unit = base
                    break

            if base_unit:
                # Check for value + any variation of the unit using regex (handles spacing)
                for variation in unit_variations.get(base_unit, [base_unit]):
                    # Regex: number, optional whitespace, unit
                    regex_pattern = rf'{re.escape(value)}\s*{re.escape(variation)}'
                    if re.search(regex_pattern, normalized_text):
                        return True

        # Fallback: just search for the numeric value followed by any common volume unit
        match = re.match(r'(\d+(?:\.\d+)?)', net_contents_lower)
        if match:
            value = match.group(1)
            # Check if value + ml/ml/l appears anywhere
            volume_pattern = rf'{re.escape(value)}\s*(ml|l|cl|oz|fl\s*oz|gal)'
            if re.search(volume_pattern, normalized_text):
                return True

        return False