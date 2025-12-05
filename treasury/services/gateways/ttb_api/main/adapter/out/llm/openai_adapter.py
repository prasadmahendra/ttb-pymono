"""OpenAI Adapter for LLM operations"""

import base64
import os
from typing import Optional, Generator
from pathlib import Path
import mimetypes

from openai import OpenAI
from openai.types.chat import ChatCompletion

from treasury.services.gateways.ttb_api.main.application.config import config
from treasury.services.gateways.ttb_api.main.application.config.config import GlobalConfig

SUPPORTED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
SUPPORTED_MEDIA_TYPES = SUPPORTED_IMAGE_TYPES | {'application/pdf'}
DEFAULT_MAX_TOKENS = 4000

class OpenAiAdapter:

    GPT_5_MINI = "gpt-5-mini"
    GPT_5_1 = "gpt-5.1"
    GPT_4O = "gpt-4o"
    DEFAULT_TEMPERATURE = 1.0

    def __init__(self, api_key: Optional[str] = None, model: str = GPT_5_1) -> None:
        self._logger = GlobalConfig.get_logger(__name__)
        self._api_key = api_key or config.OPENAI_API_KEY
        self._model = model

        if not self._api_key:
            self._logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")

        self._client = OpenAI(api_key=self._api_key)

    def complete_prompt(
            self,
            prompt: str,
            model: Optional[str] = None,
            temperature: float = DEFAULT_TEMPERATURE,
            max_tokens: Optional[int] = DEFAULT_MAX_TOKENS,
            system_prompt: Optional[str] = None
    ) -> str:
        """
        Complete a text prompt using OpenAI (non-streaming)

        Args:
            prompt: User prompt to complete
            model: Model to use (defaults to instance model)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt to set context

        Returns:
            Completion response as string

        Raises:
            Exception: If API call fails
        """
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            response: ChatCompletion = self._client.chat.completions.create(
                model=model or self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            completion_text = response.choices[0].message.content or ""

            self._logger.info(
                f"Completed prompt with {response.usage.total_tokens} tokens "
                f"(prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens})"
            )

            return completion_text

        except Exception as e:
            self._logger.error(f"Failed to complete prompt: {str(e)}")
            raise

    def complete_prompt_stream(
            self,
            prompt: str,
            model: Optional[str] = None,
            temperature: float = DEFAULT_TEMPERATURE,
            max_tokens: Optional[int] = DEFAULT_MAX_TOKENS,
            system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Complete a text prompt using OpenAI (streaming)

        Args:
            prompt: User prompt to complete
            model: Model to use (defaults to instance model)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt to set context

        Yields:
            Completion response chunks as strings

        Raises:
            Exception: If API call fails
        """
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            stream = self._client.chat.completions.create(
                model=model or self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            self._logger.error(f"Failed to stream prompt completion: {str(e)}")
            raise

    def complete_prompt_with_media(
            self,
            prompt: str,
            media_path: Optional[str] = None,
            media_base64: Optional[str] = None,
            media_url: Optional[str] = None,
            media_type: Optional[str] = None,
            model: Optional[str] = None,
            temperature: float = DEFAULT_TEMPERATURE,
            max_tokens: Optional[int] = DEFAULT_MAX_TOKENS,
            system_prompt: Optional[str] = None
    ) -> str:
        """
        Complete a prompt with media (image, PDF, etc.) using OpenAI (non-streaming)

        Args:
            prompt: User prompt to complete
            media_path: Path to media file on disk
            media_base64: Base64 encoded media (with or without data URI prefix)
            media_url: URL to media file
            media_type: MIME type of media (auto-detected for media_path)
            model: Model to use (defaults to instance model, uses gpt-4o for vision)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt to set context

        Returns:
            Completion response as string

        Raises:
            ValueError: If no media provided or unsupported media type
            Exception: If API call fails

        Note:
            Provide exactly one of: media_path, media_base64, or media_url
        """
        # Validate media input
        media_sources = [media_path, media_base64, media_url]
        if sum(x is not None for x in media_sources) != 1:
            raise ValueError("Provide exactly one of: media_path, media_base64, or media_url")

        try:
            # Prepare media content for vision model
            media_content = self._prepare_media_content(
                media_path=media_path,
                media_base64=media_base64,
                media_url=media_url,
                media_type=media_type
            )

            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Create multimodal message with text and media
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    media_content
                ]
            })

            # Use vision-capable model if not specified
            effective_model = model or self._model

            response: ChatCompletion = self._client.chat.completions.create(
                model=effective_model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens,
                stream=False
            )

            completion_text = response.choices[0].message.content or ""

            self._logger.info(
                f"Completed multimodal prompt with {response.usage.total_tokens} tokens "
                f"(prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens})"
            )

            return completion_text

        except Exception as e:
            self._logger.error(f"Failed to complete prompt with media: {str(e)}")
            raise

    def complete_prompt_with_media_stream(
            self,
            prompt: str,
            media_path: Optional[str] = None,
            media_base64: Optional[str] = None,
            media_url: Optional[str] = None,
            media_type: Optional[str] = None,
            model: Optional[str] = None,
            temperature: float = DEFAULT_TEMPERATURE,
            max_tokens: Optional[int] = DEFAULT_MAX_TOKENS,
            system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Complete a prompt with media (image, PDF, etc.) using OpenAI (streaming)

        Args:
            prompt: User prompt to complete
            media_path: Path to media file on disk
            media_base64: Base64 encoded media (with or without data URI prefix)
            media_url: URL to media file
            media_type: MIME type of media (auto-detected for media_path)
            model: Model to use (defaults to instance model, uses gpt-4o for vision)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt to set context

        Yields:
            Completion response chunks as strings

        Raises:
            ValueError: If no media provided or unsupported media type
            Exception: If API call fails

        Note:
            Provide exactly one of: media_path, media_base64, or media_url
        """
        # Validate media input
        media_sources = [media_path, media_base64, media_url]
        if sum(x is not None for x in media_sources) != 1:
            raise ValueError("Provide exactly one of: media_path, media_base64, or media_url")

        try:
            # Prepare media content for vision model
            media_content = self._prepare_media_content(
                media_path=media_path,
                media_base64=media_base64,
                media_url=media_url,
                media_type=media_type
            )

            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Create multimodal message with text and media
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    media_content
                ]
            })

            # Use vision-capable model if not specified
            effective_model = model or self._model

            stream = self._client.chat.completions.create(
                model=effective_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            self._logger.error(f"Failed to stream prompt completion with media: {str(e)}")
            raise

    def _prepare_media_content(
            self,
            media_path: Optional[str] = None,
            media_base64: Optional[str] = None,
            media_url: Optional[str] = None,
            media_type: Optional[str] = None
    ) -> dict:
        """
        Prepare media content in OpenAI API format

        Args:
            media_path: Path to media file
            media_base64: Base64 encoded media
            media_url: URL to media
            media_type: MIME type

        Returns:
            Dictionary with image_url content for OpenAI API

        Raises:
            ValueError: If media type is unsupported
            FileNotFoundError: If media_path doesn't exist
        """
        if media_url:
            # Use URL directly
            return {
                "type": "image_url",
                "image_url": {"url": media_url}
            }

        elif media_base64:
            return self._prepare_media_base64_content(media_base64, media_type)

        elif media_path:

            return self._prepare_media_file_content(media_path, media_type)

        else:
            raise ValueError("No media source provided")

    @classmethod
    def _prepare_media_base64_content(cls, media_base64: str, media_type: str) -> dict:
        # Handle base64 encoded media
        # Remove data URI prefix if present
        if media_base64.startswith('data:'):
            # Extract media type from data URI if not provided
            if not media_type and ';' in media_base64:
                media_type = media_base64.split(';')[0].replace('data:', '')
            # Extract base64 part
            if ',' in media_base64:
                media_base64 = media_base64.split(',', 1)[1]

        # Validate media type
        if media_type and media_type not in SUPPORTED_MEDIA_TYPES:
            raise ValueError(
                f"Unsupported media type: {media_type}. "
                f"Supported types: {', '.join(SUPPORTED_MEDIA_TYPES)}"
            )

        # Default to JPEG if type not specified
        media_type = media_type or 'image/jpeg'

        # Return data URI format
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{media_type};base64,{media_base64}"
            }
        }

    @classmethod
    def _prepare_media_file_content(cls, media_path, media_type) -> dict:
        # Load from file path
        path = Path(media_path)
        if not path.exists():
            raise FileNotFoundError(f"Media file not found: {media_path}")

        # Detect MIME type if not provided
        if not media_type:
            media_type, _ = mimetypes.guess_type(str(path))
            if not media_type:
                # Default based on extension
                ext = path.suffix.lower()
                if ext in ['.jpg', '.jpeg']:
                    media_type = 'image/jpeg'
                elif ext == '.png':
                    media_type = 'image/png'
                elif ext == '.gif':
                    media_type = 'image/gif'
                elif ext == '.webp':
                    media_type = 'image/webp'
                elif ext == '.pdf':
                    media_type = 'application/pdf'
                else:
                    raise ValueError(f"Could not determine media type for: {media_path}")

        # Validate media type
        if media_type not in SUPPORTED_MEDIA_TYPES:
            raise ValueError(
                f"Unsupported media type: {media_type}. "
                f"Supported types: {', '.join(SUPPORTED_MEDIA_TYPES)}"
            )

        # Read and encode file
        with open(path, 'rb') as f:
            media_bytes = f.read()
            media_base64_encoded = base64.b64encode(media_bytes).decode('utf-8')

        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{media_type};base64,{media_base64_encoded}"
            }
        }
