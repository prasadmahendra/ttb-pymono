#!/usr/bin/env python3
"""
Command-line tool to create a label approval job via the GraphQL API.

This tool sends a GraphQL mutation to create a new label approval job,
including uploading a label image from a local file.
"""

import argparse
import base64
import json
import mimetypes
import sys
from pathlib import Path
from typing import Optional

import requests


def read_image_as_base64(image_path: str) -> tuple[str, Optional[str]]:
    """
    Read an image file and convert it to base64 data URI.

    Args:
        image_path: Path to the image file

    Returns:
        Tuple of (base64_data_uri, error_message)

    Raises:
        FileNotFoundError: If the image file doesn't exist
        ValueError: If the file is not a valid image type
    """
    path = Path(image_path)

    if not path.exists():
        return "", f"Image file not found: {image_path}"

    if not path.is_file():
        return "", f"Path is not a file: {image_path}"

    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(str(path))
    if not mime_type or not mime_type.startswith('image/'):
        return "", f"File does not appear to be an image: {image_path}"

    # Validate image type (only jpg, png, gif allowed)
    allowed_types = {'image/jpeg', 'image/jpg', 'image/png', 'image/gif'}
    if mime_type not in allowed_types:
        return "", f"Image type not supported: {mime_type}. Allowed types: jpg, png, gif"

    # Read and encode the image
    try:
        with open(path, 'rb') as image_file:
            image_data = image_file.read()
            base64_encoded = base64.b64encode(image_data).decode('utf-8')

            # Normalize mime type (jpeg -> jpg for consistency)
            if mime_type == 'image/jpeg':
                mime_type = 'image/jpg'

            # Create data URI
            data_uri = f"data:{mime_type};base64,{base64_encoded}"
            return data_uri, None
    except Exception as e:
        return "", f"Error reading image file: {str(e)}"


def create_label_approval_job(
    endpoint: str,
    brand_name: str,
    product_class: str,
    alcohol_content_percentage: str,
    net_contents_in_milli_litres: str,
    label_image_base64: str,
    status: str = "pending"
) -> dict:
    """
    Call the GraphQL API to create a label approval job.

    Args:
        endpoint: GraphQL endpoint URL
        brand_name: Brand name for the product
        product_class: Product class (e.g., 'beer', 'wine', 'spirits')
        alcohol_content_percentage: Alcohol content (e.g., '5%', '12.5%')
        net_contents_in_milli_litres: Net contents in millilitres (e.g., '355', '750')
        label_image_base64: Base64 encoded image data URI
        status: Job status (default: 'pending')

    Returns:
        Response from the GraphQL API
    """
    # GraphQL mutation
    mutation = """
    mutation CreateLabelApprovalJob($input: CreateLabelApprovalJobInput!) {
        createLabelApprovalJob(input: $input) {
            success
            message
            job {
                id
                brandName
                productClass
                status
                createdAt
                jobMetadata {
                    reviewerId
                    reviewerName
                    reviewComments
                }
            }
        }
    }
    """

    # Variables for the mutation
    variables = {
        "input": {
            "status": status,
            "jobMetadata": {
                "brandName": brand_name,
                "productClass": product_class,
                "alcoholContentAbv": alcohol_content_percentage,
                "netContents": net_contents_in_milli_litres,
                "labelImageBase64": label_image_base64
            }
        }
    }

    # Prepare the request
    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "query": mutation,
        "variables": variables
    }

    try:
        # Make the request
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        return response.json()
    except requests.exceptions.ConnectionError:
        return {
            "error": f"Could not connect to GraphQL endpoint: {endpoint}",
            "suggestion": "Make sure the API server is running on the specified endpoint"
        }
    except requests.exceptions.Timeout:
        return {
            "error": "Request timed out",
            "suggestion": "The server took too long to respond"
        }
    except requests.exceptions.HTTPError as e:
        return {
            "error": f"HTTP error occurred: {e}",
            "status_code": response.status_code,
            "response": response.text
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}"
        }


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Create a label approval job via GraphQL API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a review job for a beer label
  python create_review_job.py \\
    --brand-name "Budweiser" \\
    --product-class "beer" \\
    --alcohol-content "5%" \\
    --net-contents "355" \\
    --label-image ./label.jpg

  # Create a review job for a wine label with custom endpoint
  python create_review_job.py \\
    --endpoint "http://localhost:8080/graphql" \\
    --brand-name "Château Margaux" \\
    --product-class "wine" \\
    --alcohol-content "13.5%" \\
    --net-contents "750" \\
    --label-image ./wine_label.png \\
    --status "pending"
        """
    )

    parser.add_argument(
        "--endpoint",
        default="http://localhost:8080/graphql",
        help="GraphQL endpoint URL (default: http://localhost:8080/graphql)"
    )

    parser.add_argument(
        "--brand-name",
        required=True,
        help="Brand name for the product"
    )

    parser.add_argument(
        "--product-class",
        required=True,
        choices=["beer", "wine", "spirits", "malt_beverage", "other"],
        help="Product class"
    )

    parser.add_argument(
        "--alcohol-content",
        required=True,
        help="Alcohol content percentage (e.g., '5%%', '12.5%%')"
    )

    parser.add_argument(
        "--net-contents",
        required=True,
        help="Net contents in millilitres (e.g., '355', '750')"
    )

    parser.add_argument(
        "--label-image",
        required=True,
        help="Path to the label image file (jpg, png, or gif)"
    )

    parser.add_argument(
        "--status",
        default="pending",
        choices=["pending", "approved", "rejected"],
        help="Initial job status (default: pending)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print verbose output including full request/response"
    )

    args = parser.parse_args()

    # Read and encode the image
    print(f"Reading image from: {args.label_image}")
    label_image_base64, error = read_image_as_base64(args.label_image)

    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    print(f"Image encoded successfully ({len(label_image_base64)} bytes)")

    # Create the job
    print(f"\nCreating label approval job at {args.endpoint}...")
    print(f"  Brand: {args.brand_name}")
    print(f"  Product Class: {args.product_class}")
    print(f"  Alcohol Content: {args.alcohol_content}")
    print(f"  Net Contents: {args.net_contents} mL")
    print(f"  Status: {args.status}")

    response = create_label_approval_job(
        endpoint=args.endpoint,
        brand_name=args.brand_name,
        product_class=args.product_class,
        alcohol_content_percentage=args.alcohol_content,
        net_contents_in_milli_litres=args.net_contents,
        label_image_base64=label_image_base64,
        status=args.status
    )

    # Print the response
    print("\n" + "=" * 80)

    if "error" in response:
        print("ERROR:", response.get("error"))
        if "suggestion" in response:
            print("SUGGESTION:", response.get("suggestion"))
        if args.verbose and "response" in response:
            print("\nFull response:")
            print(response.get("response"))
        sys.exit(1)

    # Pretty print the response
    if args.verbose:
        print("Full Response:")
        print(json.dumps(response, indent=2))

    # Check for GraphQL errors
    if "errors" in response:
        print("GraphQL Errors:")
        for error in response["errors"]:
            print(f"  - {error.get('message', 'Unknown error')}")
        sys.exit(1)

    # Check the mutation result
    data = response.get("data", {})
    result = data.get("createLabelApprovalJob", {})

    if result.get("success"):
        print("✓ SUCCESS")
        print(f"\nMessage: {result.get('message', 'Job created')}")

        job = result.get("job")
        if job:
            print("\nJob Details:")
            print(f"  ID: {job.get('id')}")
            print(f"  Brand: {job.get('brandName')}")
            print(f"  Product Class: {job.get('productClass')}")
            print(f"  Status: {job.get('status')}")
            print(f"  Created At: {job.get('createdAt')}")

            metadata = job.get('jobMetadata')
            if metadata:
                print("\nJob Metadata:")
                print(f"  Reviewer ID: {metadata.get('reviewerId')}")
                print(f"  Reviewer Name: {metadata.get('reviewerName')}")
                if metadata.get('reviewComments'):
                    print(f"  Comments: {', '.join(metadata.get('reviewComments'))}")
    else:
        print("✗ FAILED")
        print(f"\nMessage: {result.get('message', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()