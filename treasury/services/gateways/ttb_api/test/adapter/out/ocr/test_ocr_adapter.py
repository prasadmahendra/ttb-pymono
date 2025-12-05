import unittest
import base64
from pathlib import Path

from treasury.services.gateways.ttb_api.main.adapter.out.ocr import (
    OcrAdapter,
    OcrResult,
    OcrWord,
    OcrBlock,
    BoundingBox
)


class TestOcrAdapter(unittest.TestCase):
    """Integration tests for OCR adapter with real image processing"""

    _EXPECTED_TAQUERAY_GIN_RESULTS = {
        "full_text": "ie\n\n( rs k\nfunguany,\n\nLONDON\nDRY GIN\n\nEST? 1830",
        "blocks": [
            {
                "text": "ie",
                "lines": [
                    {
                        "text": "ie",
                        "words": [
                            {
                                "text": "ie",
                                "confidence": 26.0,
                                "bounding_box": {
                                    "x": 154,
                                    "y": 59,
                                    "width": 32,
                                    "height": 24
                                }
                            }
                        ],
                        "confidence": 26.0,
                        "bounding_box": {
                            "x": 154,
                            "y": 59,
                            "width": 32,
                            "height": 24
                        }
                    }
                ],
                "confidence": 26.0,
                "bounding_box": {
                    "x": 154,
                    "y": 59,
                    "width": 32,
                    "height": 24
                }
            },
            {
                "text": "( rs k\nfunguany,",
                "lines": [
                    {
                        "text": "( rs k",
                        "words": [
                            {
                                "text": "(",
                                "confidence": 54.0,
                                "bounding_box": {
                                    "x": 32,
                                    "y": 92,
                                    "width": 6,
                                    "height": 6
                                }
                            },
                            {
                                "text": "rs",
                                "confidence": 35.0,
                                "bounding_box": {
                                    "x": 149,
                                    "y": 76,
                                    "width": 39,
                                    "height": 15
                                }
                            },
                            {
                                "text": "k",
                                "confidence": 45.0,
                                "bounding_box": {
                                    "x": 290,
                                    "y": 92,
                                    "width": 8,
                                    "height": 15
                                }
                            }
                        ],
                        "confidence": 44.666666666666664,
                        "bounding_box": {
                            "x": 32,
                            "y": 76,
                            "width": 266,
                            "height": 31
                        }
                    },
                    {
                        "text": "funguany,",
                        "words": [
                            {
                                "text": "funguany,",
                                "confidence": 7.0,
                                "bounding_box": {
                                    "x": 53,
                                    "y": 94,
                                    "width": 243,
                                    "height": 60
                                }
                            }
                        ],
                        "confidence": 7.0,
                        "bounding_box": {
                            "x": 53,
                            "y": 94,
                            "width": 243,
                            "height": 60
                        }
                    }
                ],
                "confidence": 25.833333333333332,
                "bounding_box": {
                    "x": 32,
                    "y": 76,
                    "width": 266,
                    "height": 78
                }
            },
            {
                "text": "LONDON\nDRY GIN",
                "lines": [
                    {
                        "text": "LONDON",
                        "words": [
                            {
                                "text": "LONDON",
                                "confidence": 96.0,
                                "bounding_box": {
                                    "x": 89,
                                    "y": 170,
                                    "width": 158,
                                    "height": 25
                                }
                            }
                        ],
                        "confidence": 96.0,
                        "bounding_box": {
                            "x": 89,
                            "y": 170,
                            "width": 158,
                            "height": 25
                        }
                    },
                    {
                        "text": "DRY GIN",
                        "words": [
                            {
                                "text": "DRY",
                                "confidence": 96.0,
                                "bounding_box": {
                                    "x": 89,
                                    "y": 204,
                                    "width": 72,
                                    "height": 23
                                }
                            },
                            {
                                "text": "GIN",
                                "confidence": 96.0,
                                "bounding_box": {
                                    "x": 181,
                                    "y": 204,
                                    "width": 66,
                                    "height": 25
                                }
                            }
                        ],
                        "confidence": 96.0,
                        "bounding_box": {
                            "x": 89,
                            "y": 204,
                            "width": 158,
                            "height": 25
                        }
                    }
                ],
                "confidence": 96.0,
                "bounding_box": {
                    "x": 89,
                    "y": 170,
                    "width": 158,
                    "height": 59
                }
            },
            {
                "text": "EST? 1830",
                "lines": [
                    {
                        "text": "EST? 1830",
                        "words": [
                            {
                                "text": "EST?",
                                "confidence": 49.0,
                                "bounding_box": {
                                    "x": 128,
                                    "y": 247,
                                    "width": 35,
                                    "height": 10
                                }
                            },
                            {
                                "text": "1830",
                                "confidence": 49.0,
                                "bounding_box": {
                                    "x": 172,
                                    "y": 247,
                                    "width": 34,
                                    "height": 10
                                }
                            }
                        ],
                        "confidence": 49.0,
                        "bounding_box": {
                            "x": 128,
                            "y": 247,
                            "width": 78,
                            "height": 10
                        }
                    }
                ],
                "confidence": 49.0,
                "bounding_box": {
                    "x": 128,
                    "y": 247,
                    "width": 78,
                    "height": 10
                }
            }
        ],
        "words": [
            {
                "text": "ie",
                "confidence": 26.0,
                "bounding_box": {
                    "x": 154,
                    "y": 59,
                    "width": 32,
                    "height": 24
                }
            },
            {
                "text": "(",
                "confidence": 54.0,
                "bounding_box": {
                    "x": 32,
                    "y": 92,
                    "width": 6,
                    "height": 6
                }
            },
            {
                "text": "rs",
                "confidence": 35.0,
                "bounding_box": {
                    "x": 149,
                    "y": 76,
                    "width": 39,
                    "height": 15
                }
            },
            {
                "text": "k",
                "confidence": 45.0,
                "bounding_box": {
                    "x": 290,
                    "y": 92,
                    "width": 8,
                    "height": 15
                }
            },
            {
                "text": "funguany,",
                "confidence": 7.0,
                "bounding_box": {
                    "x": 53,
                    "y": 94,
                    "width": 243,
                    "height": 60
                }
            },
            {
                "text": "LONDON",
                "confidence": 96.0,
                "bounding_box": {
                    "x": 89,
                    "y": 170,
                    "width": 158,
                    "height": 25
                }
            },
            {
                "text": "DRY",
                "confidence": 96.0,
                "bounding_box": {
                    "x": 89,
                    "y": 204,
                    "width": 72,
                    "height": 23
                }
            },
            {
                "text": "GIN",
                "confidence": 96.0,
                "bounding_box": {
                    "x": 181,
                    "y": 204,
                    "width": 66,
                    "height": 25
                }
            },
            {
                "text": "EST?",
                "confidence": 49.0,
                "bounding_box": {
                    "x": 128,
                    "y": 247,
                    "width": 35,
                    "height": 10
                }
            },
            {
                "text": "1830",
                "confidence": 49.0,
                "bounding_box": {
                    "x": 172,
                    "y": 247,
                    "width": 34,
                    "height": 10
                }
            }
        ],
        "average_confidence": 58.90909090909091,
        "image_width": 326,
        "image_height": 457,
        "success": True,
        "error_message": None
    }

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that are shared across all tests"""
        cls.ocr = OcrAdapter()

        # Load the test image
        test_assets_dir = Path(__file__).parent.parent.parent.parent / "assets"
        image_path = test_assets_dir / "tanqueray_london_dry_gin.png"

        if not image_path.exists():
            raise FileNotFoundError(f"Test image not found: {image_path}")

        # Read and encode image
        with open(image_path, 'rb') as f:
            cls.image_bytes = f.read()
            cls.base64_image = base64.b64encode(cls.image_bytes).decode('utf-8')
            cls.base64_with_prefix = f"data:image/png;base64,{cls.base64_image}"

    def test_extract_text_success(self):
        """Test that OCR successfully extracts text from base64 image"""
        result: OcrResult = self.ocr.extract_text(self.base64_image)
        result_json = result.model_dump(mode="json")
        self.assertDictEqual(result_json, self._EXPECTED_TAQUERAY_GIN_RESULTS)

        # Verify success
        self.assertTrue(result.success, f"OCR failed: {result.error_message}")
        self.assertIsNone(result.error_message)

        # Verify full text is not empty
        self.assertIsNotNone(result.full_text)
        self.assertGreater(len(result.full_text), 0, "No text was extracted")

        # Verify image dimensions
        self.assertGreater(result.image_width, 0)
        self.assertGreater(result.image_height, 0)

        # Print extracted text for manual verification
        print("\n=== Extracted Text ===")
        print(result.full_text)
        print("=== End Text ===\n")

    def test_extract_text_with_data_uri_prefix(self):
        """Test that OCR handles base64 images with data URI prefix"""
        result = self.ocr.extract_text(self.base64_with_prefix)
        result_json = result.model_dump(mode="json")
        self.assertDictEqual(result_json, self._EXPECTED_TAQUERAY_GIN_RESULTS)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.full_text)
        self.assertGreater(len(result.full_text), 0)

    def test_extract_text_returns_words(self):
        """Test that OCR returns individual words with bounding boxes"""
        result = self.ocr.extract_text(self.base64_image)
        result_json = result.model_dump(mode="json")
        self.assertDictEqual(result_json, self._EXPECTED_TAQUERAY_GIN_RESULTS)

        # Verify words were detected
        self.assertGreater(len(result.words), 0, "No words were detected")

        # Check word count property
        self.assertEqual(result.word_count, len(result.words))

        # Verify first word structure
        first_word = result.words[0]
        self.assertIsInstance(first_word, OcrWord)
        self.assertIsNotNone(first_word.text)
        self.assertGreater(len(first_word.text), 0)
        self.assertGreaterEqual(first_word.confidence, 0.0)
        self.assertLessEqual(first_word.confidence, 100.0)
        self.assertIsInstance(first_word.bounding_box, BoundingBox)

        # Print word count and sample words
        print("\nTotal words detected: {result.word_count}")
        print("Sample words (first 10):")
        for word in result.words[:10]:
            print(f"  - '{word.text}' (confidence: {word.confidence:.1f}%)")

    def test_extract_text_returns_blocks(self):
        """Test that OCR returns text blocks (paragraphs)"""
        result = self.ocr.extract_text(self.base64_image)
        result_json = result.model_dump(mode="json")
        self.assertDictEqual(result_json, self._EXPECTED_TAQUERAY_GIN_RESULTS)

        # Verify blocks were detected
        self.assertGreater(len(result.blocks), 0, "No text blocks were detected")

        # Verify block structure
        first_block = result.blocks[0]
        self.assertIsInstance(first_block, OcrBlock)
        self.assertIsNotNone(first_block.text)
        self.assertGreater(len(first_block.text), 0)
        self.assertGreater(len(first_block.lines), 0, "Block should contain lines")
        self.assertGreaterEqual(first_block.confidence, 0.0)
        self.assertLessEqual(first_block.confidence, 100.0)
        self.assertIsInstance(first_block.bounding_box, BoundingBox)

        print(f"\nTotal blocks detected: {len(result.blocks)}")

    def test_extract_text_confidence_scores(self):
        """Test that confidence scores are calculated correctly"""
        result = self.ocr.extract_text(self.base64_image)

        # Verify average confidence is in valid range
        self.assertGreaterEqual(result.average_confidence, 0.0)
        self.assertLessEqual(result.average_confidence, 100.0)

        # Verify high/low confidence word lists
        high_conf_words = result.high_confidence_words
        low_conf_words = result.low_confidence_words

        # All high confidence words should have confidence >= 80
        for word in high_conf_words:
            self.assertGreaterEqual(word.confidence, 80.0)
            self.assertTrue(word.is_high_confidence)

        # All low confidence words should have confidence < 80
        for word in low_conf_words:
            self.assertLess(word.confidence, 80.0)
            self.assertFalse(word.is_high_confidence)

        # Total should match
        self.assertEqual(
            len(high_conf_words) + len(low_conf_words),
            result.word_count
        )

        print(f"\nAverage confidence: {result.average_confidence:.2f}%")
        print(f"High confidence words: {len(high_conf_words)}")
        print(f"Low confidence words: {len(low_conf_words)}")

    def test_extract_text_bounding_boxes(self):
        """Test that bounding boxes have valid coordinates"""
        result = self.ocr.extract_text(self.base64_image)

        for word in result.words:
            bbox = word.bounding_box

            # Verify coordinates are non-negative
            self.assertGreaterEqual(bbox.x, 0)
            self.assertGreaterEqual(bbox.y, 0)
            self.assertGreater(bbox.width, 0)
            self.assertGreater(bbox.height, 0)

            # Verify x2/y2 properties
            self.assertEqual(bbox.x2, bbox.x + bbox.width)
            self.assertEqual(bbox.y2, bbox.y + bbox.height)

            # Verify coordinates are within image bounds
            self.assertLessEqual(bbox.x2, result.image_width)
            self.assertLessEqual(bbox.y2, result.image_height)

    def test_extract_text_hierarchical_structure(self):
        """Test that blocks contain lines and lines contain words"""
        result = self.ocr.extract_text(self.base64_image)

        for block in result.blocks:
            # Verify block has lines
            self.assertGreater(len(block.lines), 0, "Block should contain at least one line")

            for line in block.lines:
                # Verify line has words
                self.assertGreater(len(line.words), 0, "Line should contain at least one word")

                # Verify line text is concatenation of word texts
                expected_line_text = ' '.join(w.text for w in line.words)
                self.assertEqual(line.text, expected_line_text)

                # Verify all words in line are also in result.words
                for word in line.words:
                    self.assertIn(word, result.words)

    def test_extract_text_expected_content(self):
        """Test that OCR extracts expected text from Tanqueray gin label"""
        result = self.ocr.extract_text(self.base64_image)

        full_text_lower = result.full_text.lower()

        # Expected text that should appear on a Tanqueray London Dry Gin label
        # Note: OCR may not be perfect, so we check for key terms
        expected_terms = ['tanqueray', 'london', 'gin']

        found_terms = []
        for term in expected_terms:
            if term in full_text_lower:
                found_terms.append(term)

        # At least one expected term should be found
        self.assertGreater(
            len(found_terms), 0,
            f"Expected to find at least one of {expected_terms} in extracted text"
        )

        print(f"\nFound expected terms: {found_terms}")

    def test_extract_text_invalid_base64(self):
        """Test that OCR handles invalid base64 gracefully"""
        result = self.ocr.extract_text("not-valid-base64")

        # Should fail gracefully
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertEqual(len(result.words), 0)
        self.assertEqual(len(result.blocks), 0)
        self.assertEqual(result.full_text, "")

    def test_extract_text_empty_string(self):
        """Test that OCR handles empty string gracefully"""
        result = self.ocr.extract_text("")

        # Should fail gracefully
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)


if __name__ == '__main__':
    unittest.main()
