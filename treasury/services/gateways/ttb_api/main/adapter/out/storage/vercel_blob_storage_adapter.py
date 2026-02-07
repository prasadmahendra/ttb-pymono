"""Vercel Blob Storage adapter for uploading images"""

import os
import uuid
from typing import Optional

import requests

from treasury.services.gateways.ttb_api.main.application.config.config import GlobalConfig


class VercelBlobStorageAdapter:

    VERCEL_BLOB_API_URL = "https://blob.vercel-storage.com"

    def __init__(self, token: Optional[str] = None) -> None:
        self._logger = GlobalConfig.get_logger(__name__)
        self._token = token or os.environ.get("BLOB_READ_WRITE_TOKEN")
        if not self._token:
            self._logger.warning("No BLOB_READ_WRITE_TOKEN provided. Vercel Blob uploads will fail.")

    def upload_image(self, image_data: bytes, filename: str, content_type: str) -> str:
        """
        Upload an image to Vercel Blob Storage.

        Args:
            image_data: Raw image bytes
            filename: Desired filename (will be prefixed with a unique path)
            content_type: MIME type of the image (e.g., 'image/jpeg')

        Returns:
            Public URL of the uploaded blob

        Raises:
            RuntimeError: If upload fails
        """
        # Generate a unique path to avoid collisions
        unique_filename = f"label-images/{uuid.uuid4()}/{filename}"

        headers = {
            "Authorization": f"Bearer {self._token}",
            "x-content-type": content_type,
            "x-api-version": "7",
        }

        try:
            response = requests.put(
                f"{self.VERCEL_BLOB_API_URL}/{unique_filename}",
                headers=headers,
                data=image_data,
                timeout=60,
            )
            response.raise_for_status()

            result = response.json()
            url = result.get("url")
            if not url:
                raise RuntimeError(f"Vercel Blob response missing 'url': {result}")

            self._logger.info(f"Uploaded image to Vercel Blob: {url}")
            return url

        except requests.RequestException as e:
            self._logger.error(f"Failed to upload image to Vercel Blob: {str(e)}")
            raise RuntimeError(f"Failed to upload image to Vercel Blob: {str(e)}") from e
