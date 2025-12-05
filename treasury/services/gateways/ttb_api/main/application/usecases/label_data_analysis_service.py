from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import LabelApprovalJob
from treasury.services.gateways.ttb_api.main.application.models.domain.label_extraction_data import BrandDataStrict, \
    ProductInfoStrict, ProductOtherInfo
from treasury.services.gateways.ttb_api.main.application.usecases.label_data_extraction_service import \
    LabelDataExtractionService


class LabelDataAnalysisService:
    _USE_LLM: bool = True # If set to False we use Tesseract OCR for analysis

    def __init__(self, label_data_extraction_service: LabelDataExtractionService = None) -> None:
        self._label_data_extraction_service_lazy = label_data_extraction_service

    @property
    def _label_data_extraction_service(self) -> LabelDataExtractionService:
        if self._label_data_extraction_service_lazy is None:
            self._label_data_extraction_service_lazy = LabelDataExtractionService()
        return self._label_data_extraction_service_lazy

    def analyze_label_data(self, job: LabelApprovalJob) -> LabelApprovalJob:
        job_meta = job.get_job_metadata()
        stated_product_info: BrandDataStrict = job_meta.product_info
        # job.get_job_metadata().bottler_info