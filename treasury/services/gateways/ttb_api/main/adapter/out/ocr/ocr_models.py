"""Pydantic models for OCR results"""

from typing import Optional, List
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box coordinates for detected text"""
    x: int = Field(..., description="X coordinate of top-left corner")
    y: int = Field(..., description="Y coordinate of top-left corner")
    width: int = Field(..., description="Width of bounding box")
    height: int = Field(..., description="Height of bounding box")

    @property
    def x2(self) -> int:
        """X coordinate of bottom-right corner"""
        return self.x + self.width

    @property
    def y2(self) -> int:
        """Y coordinate of bottom-right corner"""
        return self.y + self.height


class OcrWord(BaseModel):
    """Single word detected by OCR"""
    text: str = Field(..., description="Detected text content")
    confidence: float = Field(..., ge=0.0, le=100.0, description="Confidence score (0-100)")
    bounding_box: BoundingBox = Field(..., description="Bounding box coordinates")

    @property
    def is_high_confidence(self) -> bool:
        """Check if confidence is above 80%"""
        return self.confidence >= 80.0


class OcrLine(BaseModel):
    """Line of text detected by OCR"""
    text: str = Field(..., description="Full line text")
    words: List[OcrWord] = Field(default_factory=list, description="Individual words in the line")
    confidence: float = Field(..., ge=0.0, le=100.0, description="Average confidence for the line")
    bounding_box: BoundingBox = Field(..., description="Bounding box for entire line")


class OcrBlock(BaseModel):
    """Block/paragraph of text detected by OCR"""
    text: str = Field(..., description="Full block text")
    lines: List[OcrLine] = Field(default_factory=list, description="Lines in the block")
    confidence: float = Field(..., ge=0.0, le=100.0, description="Average confidence for the block")
    bounding_box: BoundingBox = Field(..., description="Bounding box for entire block")


class OcrResult(BaseModel):
    """Complete OCR result for an image"""
    full_text: str = Field(..., description="All detected text concatenated")
    blocks: List[OcrBlock] = Field(default_factory=list, description="Text blocks detected")
    words: List[OcrWord] = Field(default_factory=list, description="All words detected")
    average_confidence: float = Field(..., ge=0.0, le=100.0, description="Average confidence across all text")
    image_width: int = Field(..., description="Width of processed image in pixels")
    image_height: int = Field(..., description="Height of processed image in pixels")
    success: bool = Field(default=True, description="Whether OCR was successful")
    error_message: Optional[str] = Field(None, description="Error message if OCR failed")

    @property
    def word_count(self) -> int:
        """Total number of words detected"""
        return len(self.words)

    @property
    def high_confidence_words(self) -> List[OcrWord]:
        """Words with confidence >= 80%"""
        return [word for word in self.words if word.is_high_confidence]

    @property
    def low_confidence_words(self) -> List[OcrWord]:
        """Words with confidence < 80%"""
        return [word for word in self.words if not word.is_high_confidence]