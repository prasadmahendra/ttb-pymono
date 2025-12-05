"""Integration tests for LabelDataExtractionService using real OpenAI API"""

import unittest
import base64
from pathlib import Path

from treasury.services.gateways.ttb_api.main.application.config import config
from treasury.services.gateways.ttb_api.main.application.usecases.label_data_extraction_service import (
    LabelDataExtractionService
)
from treasury.services.gateways.ttb_api.main.application.models.domain.label_extraction_data import (
    BrandDataStrict,
)


def is_openai_api_key_available():
    """Check if OpenAI API key is available"""
    # Disabled!
    return False
    # return config.OPENAI_API_KEY is not None


@unittest.skipUnless(
    is_openai_api_key_available(),
    "OpenAI API key not found. Set OPENAI_API_KEY environment variable to run integration tests."
)
class TestLabelDataExtractionService(unittest.TestCase):
    """Integration tests for label data extraction using real OpenAI API

    Note: These tests require an OpenAI API key and will make real API calls.
    Set the OPENAI_API_KEY environment variable to run these tests.
    """

    _EXPECTED_OUTPUT = {
        "brand_name":"Tanqueray",
        "products":[
            {
                "alcohol_content_abv":"41.3%",
                "name":"Tanqueray London Dry Gin",
                "net_contents":"70 cL",
                "other_info":{
                    "bottler_info":"Produced & Bottled in Great Britain",
                    "manufacturer":"Charles Tanqueray & Co",
                    "warnings":"Unknown"
                },
                "product_class_type":"London Dry Gin"
            }
        ]
    }

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures shared across all tests"""
        # Initialize service with real OpenAI adapter
        cls.service = LabelDataExtractionService()

        # Load the test image
        test_assets_dir = Path(__file__).parent.parent.parent / "assets"
        image_path = test_assets_dir / "tanqueray_london_dry_gin.png"

        if not image_path.exists():
            raise FileNotFoundError(f"Test image not found: {image_path}")

        # Read and encode image
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
            cls.base64_image = base64.b64encode(image_bytes).decode('utf-8')
            cls.base64_with_prefix = f"data:image/png;base64,{cls.base64_image}"

    def test_extract_label_data_success(self):
        """Test that label data extraction returns valid BrandDataStrict object"""
        result = self.service.extract_label_data(self.base64_image)

        self.maxDiff = None  # Show full diff on failure
        self.assertIsNotNone(result)
        jj = result.model_dump(mode="json")
        self.assertDictEqual(self._EXPECTED_OUTPUT, result.model_dump(mode="json"))

        # Verify result is correct type
        self.assertIsInstance(result, BrandDataStrict)

        # Verify brand_name is populated
        self.assertIsNotNone(result.brand_name)
        self.assertGreater(len(result.brand_name), 0)

        print("\n=== Extracted Brand Data ===")
        print(f"Brand Name: {result.brand_name}")
        print(f"Number of Products: {len(result.products)}")

    def test_extract_label_data_with_data_uri_prefix(self):
        """Test that extraction works with data URI prefix"""
        result = self.service.extract_label_data(self.base64_with_prefix)

        # Verify result is valid
        self.assertIsInstance(result, BrandDataStrict)
        self.assertIsNotNone(result.brand_name)
        self.assertGreater(len(result.brand_name), 0)


if __name__ == '__main__':
    unittest.main()
