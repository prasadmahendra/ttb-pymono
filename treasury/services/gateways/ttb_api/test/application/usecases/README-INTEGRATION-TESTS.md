# Integration Tests for Label Data Extraction Service

This directory contains integration tests for the `LabelDataExtractionService` that make real API calls to OpenAI.

## Prerequisites

### 1. OpenAI API Key

These tests require a valid OpenAI API key with access to GPT-4 Vision models.

**Set your API key:**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

Or add it to your `.env` file:
```bash
OPENAI_API_KEY=your-api-key-here
```

### 2. Required Packages

Ensure you have the required packages installed:
```bash
pip install openai pydantic pillow
```

## Running the Tests

### Run all integration tests:
```bash
python -m pytest treasury/services/gateways/ttb_api/test/application/usecases/test_label_data_extraction_service.py -v
```

### Run with output:
```bash
python -m pytest treasury/services/gateways/ttb_api/test/application/usecases/test_label_data_extraction_service.py -v -s
```

### Run a specific test:
```bash
python -m pytest treasury/services/gateways/ttb_api/test/application/usecases/test_label_data_extraction_service.py::TestLabelDataExtractionService::test_extract_label_data_success -v -s
```

### Skip if API key not available:
The tests will automatically skip if no OpenAI API key is found:
```
SKIPPED [1] test_label_data_extraction_service.py:22: OpenAI API key not found. Set OPENAI_API_KEY environment variable to run integration tests.
```

## Test Coverage

The integration tests cover:

1. **Basic Extraction** - Verifies label data can be extracted from images
2. **Data URI Support** - Tests base64 images with/without data URI prefix
3. **Product Information** - Validates all required product fields are extracted
4. **Format Validation** - Ensures ABV and volume follow required patterns:
   - ABV: `"41%"` or `"41.3%"`
   - Volume: `"700 mL"`, `"70 cL"`, or `"12 fl oz"`
5. **Structured Data** - Verifies other_info fields (producer, origin, warnings, etc.)
6. **Content Validation** - Checks expected terms are found for known labels
7. **Consistency** - Tests multiple calls return consistent structure
8. **Custom Adapter** - Verifies service works with custom OpenAI adapter

## Test Image

Tests use: `treasury/services/gateways/ttb_api/test/assets/tanqueray_london_dry_gin.png`

This is a sample product label image used for testing the extraction capabilities.

## Important Notes

⚠️ **API Costs**: These tests make real API calls to OpenAI and will incur costs based on your OpenAI pricing plan.

⚠️ **Rate Limits**: Running tests multiple times may hit API rate limits. Add delays if needed.

⚠️ **Non-Deterministic**: LLM responses may vary slightly between runs, though the structure should remain consistent.

## Example Output

```
test_extract_label_data_success PASSED

=== Extracted Brand Data ===
Brand Name: Tanqueray
Number of Products: 1

=== First Product Details ===
Name: Tanqueray London Dry Gin
Class: Distilled Spirits
ABV: 47.3%
Volume: 750 mL

=== Other Product Info ===
Description: A classic London Dry Gin...
Producer: Tanqueray Gordon & Co.
Origin: Scotland
Bottler: Charles Tanqueray & Co.
Manufacturer: Diageo
Warnings: GOVERNMENT WARNING: According to the Surgeon General...
```

## Troubleshooting

### Tests are skipped:
- Check that `OPENAI_API_KEY` is set: `echo $OPENAI_API_KEY`
- Verify the key is valid

### Authentication errors:
- Verify your API key is correct
- Check your OpenAI account status and billing

### Validation errors:
- The LLM may return data in a slightly different format
- Check logs for the raw LLM response
- May need to adjust the prompt or validation logic

### Rate limit errors:
- Wait a few minutes before running tests again
- Consider adding delays between tests
- Check your OpenAI account rate limits