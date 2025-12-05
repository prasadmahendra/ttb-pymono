from typing import Optional

from treasury.services.gateways.ttb_api.main.adapter.out.llm.openai_adapter import OpenAiAdapter
from treasury.services.gateways.ttb_api.main.application.config.config import GlobalConfig
from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import LabelApprovalJob, \
    LabelImageAnalysisResult, LabelImage, JobMetadata
from treasury.services.gateways.ttb_api.main.application.models.domain.label_extraction_data import BrandDataStrict
from treasury.services.gateways.ttb_api.main.application.usecases.label_data_extraction import \
    LabelDataExtractionService
from treasury.services.gateways.ttb_api.main.application.usecases.llm_prompts import LlmPrompts


class LabelDataAnalysisService:
    _USE_LLM: bool = True # If set to False we use Tesseract OCR for analysis

    def __init__(
            self,
            label_data_extraction_service: LabelDataExtractionService = None,
            openai_adapter: OpenAiAdapter = None
    ) -> None:
        self._label_data_extraction_service_lazy = label_data_extraction_service
        self._openai_adapter_lazy = openai_adapter
        self._logger = GlobalConfig.get_logger(__name__)

    @property
    def _openai_adapter(self) -> OpenAiAdapter:
        if self._openai_adapter_lazy is None:
            self._openai_adapter_lazy = OpenAiAdapter()
        return self._openai_adapter_lazy

    @property
    def _label_data_extraction_service(self) -> LabelDataExtractionService:
        if self._label_data_extraction_service_lazy is None:
            self._label_data_extraction_service_lazy = LabelDataExtractionService()
        return self._label_data_extraction_service_lazy

    def analyze_label_data(self, job: LabelApprovalJob) -> Optional[LabelApprovalJob]:
        job_meta = job.get_job_metadata()

        if not job_meta.label_images or len(job_meta.label_images) == 0:
            return None

        try:
            # TODO: There can be multiple images, for now we analyze only the first one
            image_to_analyze = job_meta.label_images[0]
            extracted_label_data: BrandDataStrict = self._label_data_extraction_service.extract_label_data(
                base64_image=image_to_analyze.base64
            )

            # inputs are immutable ... clone and update
            job_clone = LabelApprovalJob.model_validate(job.model_dump())
            job_metadata_clone = job_clone.get_job_metadata()

            image_to_analyze_with_ext_data = image_to_analyze.model_copy(deep=True) # Inefficient since we keep the base64 image in here!
            image_to_analyze_with_ext_data.extracted_product_info = extracted_label_data

            # replace the first image with the updated one
            job_metadata_clone.label_images[0] = image_to_analyze_with_ext_data
            job_clone.job_metadata = job_metadata_clone

            job_clone: Optional[LabelApprovalJob] = self.answer_analysis_questions(job=job_clone, image_to_analyze=image_to_analyze_with_ext_data)
            if job_clone is None:
                self._logger.warning(f"Label analysis failed for job={job.id}")
                return None

            return job_clone
        except Exception as e:
            # gracefully handle errors
            self._logger.exception(f"Error during label data extraction job={job.id} error={e}")
            return None

    def answer_analysis_questions(self, job: LabelApprovalJob, image_to_analyze: LabelImage) -> Optional[LabelApprovalJob]:
        """Analyze the extracted label data and answer the analysis questions"""

        given_brand_label_info = job.get_job_metadata().product_info
        extracted_brand_label_info = image_to_analyze.extracted_product_info

        prompt: str = LlmPrompts.get_label_analysis_prompt(
            given_brand_label_info=given_brand_label_info,
            extracted_brand_label_info=extracted_brand_label_info,
        )

        try:
            response: str = self._openai_adapter.complete_prompt(
                prompt=prompt,
            )
            self._logger.info(f"Label analysis response={response}")
            # json cleanup
            response_cleaned: dict = LabelDataExtractionService.extract_json_from_response(response)
            # parse response
            analysis_result: LabelImageAnalysisResult = LabelImageAnalysisResult.model_validate(response_cleaned)

            # inputs are immutable ... clone and update
            job_clone = LabelApprovalJob.model_validate(job.model_dump())
            job_metadata_clone: JobMetadata = job_clone.get_job_metadata()

            image_to_analyze_clone: LabelImage = image_to_analyze.model_copy(deep=True) # Inefficient since we keep the base64 image in here!

            # replace the first image with the updated one
            job_metadata_clone.label_images[0] = image_to_analyze_clone
            image_to_analyze_clone.analysis_result = analysis_result

            job_clone.job_metadata = job_metadata_clone
            return job_clone
        except Exception as e:
            # gracefully handle errors
            self._logger.exception(f"answer_analysis_questions - Error during label data extraction job={job.id} error={e}")
            return None

