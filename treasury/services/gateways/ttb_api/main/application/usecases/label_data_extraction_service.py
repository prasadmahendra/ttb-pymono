import json
import re

from treasury.services.gateways.ttb_api.main.adapter.out.llm.openai_adapter import OpenAiAdapter
from treasury.services.gateways.ttb_api.main.application.config.config import GlobalConfig
from treasury.services.gateways.ttb_api.main.application.models.domain.label_extraction_data import BrandDataStrict
from treasury.services.gateways.ttb_api.main.application.usecases.llm_prompts import LlmPrompts


class LabelDataExtractionService:
    def __init__(self, llm_client: OpenAiAdapter = None) -> None:
        self._llm_client_lazy = llm_client
        self._logger = GlobalConfig.get_logger(__name__)

    @property
    def _llm_client(self) -> OpenAiAdapter:
        if self._llm_client_lazy is None:
            self._llm_client_lazy = OpenAiAdapter()
        return self._llm_client_lazy

    def extract_label_data(self, base64_image: str) -> BrandDataStrict:
        llm_results: str = self._llm_client.complete_prompt_with_media(
            prompt=LlmPrompts.TTB_LABEL_IMAGE_INQUIRY_PROMPT,
            media_base64=base64_image,
        )
        self._logger.info(f"extract_label_data - LLM Results for base64_image: {llm_results}")

        # Parse JSON from LLM response (may include markdown code blocks)
        json_data = self._extract_json_from_response(llm_results)

        # Validate and parse into Pydantic model
        results = BrandDataStrict.model_validate(json_data)
        return results

    def _extract_json_from_response(self, response: str) -> dict:
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
            self._logger.error(f"Failed to parse JSON from LLM response: {str(e)}")
            self._logger.error(f"Response: {response}")
            raise ValueError(f"Could not parse JSON from LLM response: {str(e)}")

