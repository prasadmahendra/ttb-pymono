"""OCR Adapter Module"""

from treasury.services.gateways.ttb_api.main.adapter.out.ocr.ocr_adapter import OcrAdapter
from treasury.services.gateways.ttb_api.main.adapter.out.ocr.ocr_models import (
    BoundingBox,
    OcrWord,
    OcrLine,
    OcrBlock,
    OcrResult
)

__all__ = [
    'OcrAdapter',
    'BoundingBox',
    'OcrWord',
    'OcrLine',
    'OcrBlock',
    'OcrResult'
]