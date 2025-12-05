# TTB API Command-Line Tools

This directory contains command-line tools for interacting with the TTB API GraphQL endpoint.

## Tools

### `create_review_job.py`

A command-line tool to create label approval jobs via the GraphQL API. This tool allows you to submit product label information and images for review.

## Installation

Make sure you have the required dependencies installed:

```bash
pip install requests
```

Or if using the project's virtual environment:

```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

## Usage

### Basic Usage

```bash
python create_review_job.py \
  --brand-name "Your Brand Name" \
  --product-class "beer" \
  --alcohol-content "5%" \
  --net-contents "355" \
  --label-image /path/to/label.jpg
```

### Command-Line Options

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `--endpoint` | No | GraphQL endpoint URL | `http://localhost:8080/graphql` |
| `--brand-name` | Yes | Brand name for the product | - |
| `--product-class` | Yes | Product class: `beer`, `wine`, `spirits`, `malt_beverage`, `other` | - |
| `--alcohol-content` | Yes | Alcohol content percentage (e.g., `5%`, `12.5%`) | - |
| `--net-contents` | Yes | Net contents in millilitres (e.g., `355`, `750`) | - |
| `--label-image` | Yes | Path to the label image file (jpg, png, or gif) | - |
| `--status` | No | Initial job status: `pending`, `approved`, `rejected` | `pending` |
| `--verbose`, `-v` | No | Print verbose output including full request/response | - |

## Examples

### Example 1: Create a Beer Label Review Job

```bash
python create_review_job.py \
  --brand-name "Budweiser" \
  --product-class "beer" \
  --alcohol-content "5%" \
  --net-contents "355" \
  --label-image ./examples/budweiser_label.jpg
```

**Expected Output:**
```
Reading image from: ./examples/budweiser_label.jpg
Image encoded successfully (125432 bytes)

Creating label approval job at http://localhost:8080/graphql...
  Brand: Budweiser
  Product Class: beer
  Alcohol Content: 5%
  Net Contents: 355 mL
  Status: pending

================================================================================
✓ SUCCESS

Message: Label approval job created successfully

Job Details:
  ID: 550e8400-e29b-41d4-a716-446655440000
  Brand: Budweiser
  Product Class: beer
  Status: pending
  Created At: 2025-12-05T10:30:00Z

Job Metadata:
  Reviewer ID: 123e4567-e89b-12d3-a456-426614174000
  Reviewer Name: John Doe
  Comments: Review initiated
```

### Example 2: Create a Wine Label Review Job

```bash
python create_review_job.py \
  --brand-name "Château Margaux" \
  --product-class "wine" \
  --alcohol-content "13.5%" \
  --net-contents "750" \
  --label-image ./examples/margaux_label.png
```

### Example 3: Create a Spirits Label Review Job

```bash
python create_review_job.py \
  --brand-name "Jack Daniel's" \
  --product-class "spirits" \
  --alcohol-content "40%" \
  --net-contents "700" \
  --label-image ./examples/jack_daniels_label.jpg
```

### Example 4: Using a Custom Endpoint

```bash
python create_review_job.py \
  --endpoint "https://api.example.com/graphql" \
  --brand-name "Corona Extra" \
  --product-class "beer" \
  --alcohol-content "4.6%" \
  --net-contents "355" \
  --label-image ./corona_label.jpg
```

### Example 5: Verbose Output

For debugging or to see the full GraphQL request/response:

```bash
python create_review_job.py \
  --brand-name "Heineken" \
  --product-class "beer" \
  --alcohol-content "5%" \
  --net-contents "330" \
  --label-image ./heineken_label.jpg \
  --verbose
```

### Example 6: Using Environment Variables

You can combine this tool with environment variables for easier usage:

```bash
# Set the endpoint
export TTB_API_ENDPOINT="http://localhost:8080/graphql"

# Create the job
python create_review_job.py \
  --endpoint "$TTB_API_ENDPOINT" \
  --brand-name "Sierra Nevada Pale Ale" \
  --product-class "beer" \
  --alcohol-content "5.6%" \
  --net-contents "355" \
  --label-image ./sierra_nevada_label.jpg
```

## Image Requirements

The tool accepts label images with the following specifications:

- **Supported formats**: JPG, PNG, GIF
- **File size**: Any reasonable size (will be base64 encoded)
- **Validation**: Images are validated for proper format and encoding

## Error Handling

The tool provides clear error messages for common issues:

### Image File Not Found
```
Error: Image file not found: ./nonexistent.jpg
```

### Invalid Image Type
```
Error: Image type not supported: image/bmp. Allowed types: jpg, png, gif
```

### Connection Error
```
ERROR: Could not connect to GraphQL endpoint: http://localhost:8080/graphql
SUGGESTION: Make sure the API server is running on the specified endpoint
```

### GraphQL Validation Error
```
GraphQL Errors:
  - Brand name and product class are required in job metadata
```

### Invalid Alcohol Content
```
✗ FAILED

Message: Invalid alcohol content percentage: Alcohol content must be between 0% and 100%
```

## Tips and Best practices

1. **Test the endpoint first**: Make sure your API server is running before using the tool:
   ```bash
   curl http://localhost:8080/graphql
   ```

2. **Use absolute paths**: For label images, use absolute paths to avoid confusion:
   ```bash
   python create_review_job.py \
     --label-image "$(pwd)/label.jpg" \
     ...
   ```

3. **Check image size**: Very large images will be encoded to base64, which increases size by ~33%. Consider resizing large images before upload.

4. **Save responses**: Use verbose mode and redirect output to save full responses:
   ```bash
   python create_review_job.py ... --verbose > response.json
   ```

5. **Batch processing**: Create a script to process multiple labels:
   ```bash
   #!/bin/bash
   for label in labels/*.jpg; do
     python create_review_job.py \
       --brand-name "$(basename "$label" .jpg)" \
       --product-class "beer" \
       --alcohol-content "5%" \
       --net-contents "355" \
       --label-image "$label"
   done
   ```

## Troubleshooting

### "Module not found: requests"

Install the requests library:
```bash
pip install requests
```

### "Permission denied"

Make the script executable:
```bash
chmod +x create_review_job.py
```

Then run it directly:
```bash
./create_review_job.py --brand-name "..." ...
```

### "Connection refused"

The API server is not running. Start the server:
```bash
# From the project root
python -m treasury.services.gateways.ttb_api.main.app
```

### GraphQL Mutation Errors

Check the API logs for detailed error messages. Common issues:
- Missing required fields
- Invalid alcohol content format (must include `%` symbol)
- Invalid net contents format (must be a positive number)
- Authentication/authorization issues (if enabled)

## Development

To modify or extend the tool:

1. The GraphQL mutation is defined in the `create_label_approval_job()` function
2. Image encoding happens in the `read_image_as_base64()` function
3. Command-line argument parsing is in the `main()` function

## Related Documentation

- GraphQL Schema: See `treasury/services/gateways/ttb_api/main/application/models/gql/label_approvals/`
- API Documentation: See the main API README
- Testing: See the test files in `treasury/services/gateways/ttb_api/test/`