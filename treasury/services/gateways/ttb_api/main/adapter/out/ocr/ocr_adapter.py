"""OCR Adapter using Tesseract for text extraction from images"""

import base64
import io
from typing import Optional, Dict, List, Literal
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import requests

from treasury.services.gateways.ttb_api.main.adapter.out.ocr.ocr_models import (
    OcrResult,
    OcrBlock,
    OcrLine,
    OcrWord,
    BoundingBox
)

from treasury.services.gateways.ttb_api.main.application.config.config import GlobalConfig

# Constants
DATA_URI_PREFIX = 'data:image'


class OcrAdapter:

    def __init__(self, tesseract_cmd: Optional[str] = None):
        self._logger = GlobalConfig.get_logger(__name__)
        # Set tesseract command path if provided
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text_from_url(self, image_url: str) -> OcrResult:
        try:
            # Download image from URL
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # Convert to PIL Image
            image = Image.open(io.BytesIO(response.content))

            # Process with OCR
            return self._process_image(image)

        except requests.RequestException as e:
            self._logger.error(f"Failed to download image from {image_url}: {str(e)}")
            return OcrResult(
                full_text="",
                blocks=[],
                words=[],
                average_confidence=0.0,
                image_width=0,
                image_height=0,
                success=False,
                error_message=f"Failed to download image: {str(e)}"
            )
        except Exception as e:
            self._logger.error(f"Failed to process image from URL: {str(e)}")
            return OcrResult(
                full_text="",
                blocks=[],
                words=[],
                average_confidence=0.0,
                image_width=0,
                image_height=0,
                success=False,
                error_message=f"OCR processing failed: {str(e)}"
            )

    def extract_text(self, base64_encoded_image: str) -> OcrResult:
        try:
            # Remove data URI prefix if present
            if base64_encoded_image.startswith(DATA_URI_PREFIX):
                # Format: data:image/jpeg;base64,/9j/4AAQ...
                base64_encoded_image = base64_encoded_image.split(',', 1)[1]

            # Decode base64 to bytes
            image_bytes = base64.b64decode(base64_encoded_image)

            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            # Process with OCR
            return self._process_image(image)

        except Exception as e:
            self._logger.error(f"Failed to process base64 image: {str(e)}")
            return OcrResult(
                full_text="",
                blocks=[],
                words=[],
                average_confidence=0.0,
                image_width=0,
                image_height=0,
                success=False,
                error_message=f"Failed to decode/process image: {str(e)}"
            )

    def _process_image(self, image: Image.Image) -> OcrResult:
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Get image dimensions
            width, height = image.size

            # Get detailed OCR data
            # Output includes: level, page_num, block_num, par_num, line_num, word_num,
            # left, top, width, height, conf, text
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            # Parse OCR data into structured format
            words, blocks = self._parse_ocr_data(ocr_data)

            # Get full text
            full_text = pytesseract.image_to_string(image).strip()

            # Calculate average confidence (excluding -1 confidence values)
            confidences = [float(conf) for conf in ocr_data['conf'] if int(conf) != -1]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return OcrResult(
                full_text=full_text,
                blocks=blocks,
                words=words,
                average_confidence=avg_confidence,
                image_width=width,
                image_height=height,
                success=True,
                error_message=None
            )

        except pytesseract.TesseractNotFoundError:
            self._logger.error("Tesseract not found. Please install tesseract-ocr.")
            return OcrResult(
                full_text="",
                blocks=[],
                words=[],
                average_confidence=0.0,
                image_width=0,
                image_height=0,
                success=False,
                error_message="Tesseract OCR not installed or not found in PATH"
            )
        except Exception as e:
            self._logger.error(f"OCR processing failed: {str(e)}")
            return OcrResult(
                full_text="",
                blocks=[],
                words=[],
                average_confidence=0.0,
                image_width=0,
                image_height=0,
                success=False,
                error_message=f"OCR processing error: {str(e)}"
            )

    def _parse_ocr_data(self, ocr_data: Dict) -> tuple[List[OcrWord], List[OcrBlock]]:
        all_words: List[OcrWord] = []
        lines_dict: Dict[tuple, Dict] = {}

        n_boxes = len(ocr_data['text'])

        for i in range(n_boxes):
            # Skip empty text and invalid confidence
            text = str(ocr_data['text'][i]).strip()
            conf = int(ocr_data['conf'][i])

            if not text or conf == -1:
                continue

            # Extract position data
            level = int(ocr_data['level'][i])
            block_num = int(ocr_data['block_num'][i])
            par_num = int(ocr_data['par_num'][i])
            line_num = int(ocr_data['line_num'][i])

            left = int(ocr_data['left'][i])
            top = int(ocr_data['top'][i])
            width = int(ocr_data['width'][i])
            height = int(ocr_data['height'][i])

            bounding_box = BoundingBox(x=left, y=top, width=width, height=height)

            # Level 5 is word level
            if level == 5:
                word = OcrWord(
                    text=text,
                    confidence=float(conf),
                    bounding_box=bounding_box
                )
                all_words.append(word)

                # Organize by line
                line_key = (block_num, par_num, line_num)
                if line_key not in lines_dict:
                    lines_dict[line_key] = {
                        'words': [],
                        'block_num': block_num,
                        'par_num': par_num
                    }
                lines_dict[line_key]['words'].append(word)

        # Build lines and blocks
        blocks: List[OcrBlock] = []

        # Group lines by block
        block_lines: Dict[int, List[OcrLine]] = {}

        for line_key, line_data in lines_dict.items():
            block_num, par_num, line_num = line_key
            words = line_data['words']

            if not words:
                continue

            # Calculate line bounding box
            min_x = min(w.bounding_box.x for w in words)
            min_y = min(w.bounding_box.y for w in words)
            max_x = max(w.bounding_box.x2 for w in words)
            max_y = max(w.bounding_box.y2 for w in words)

            line_bbox = BoundingBox(
                x=min_x,
                y=min_y,
                width=max_x - min_x,
                height=max_y - min_y
            )

            # Calculate average confidence for line
            line_conf = sum(w.confidence for w in words) / len(words)

            # Concatenate text
            line_text = ' '.join(w.text for w in words)

            line = OcrLine(
                text=line_text,
                words=words,
                confidence=line_conf,
                bounding_box=line_bbox
            )

            if block_num not in block_lines:
                block_lines[block_num] = []
            block_lines[block_num].append(line)

        # Build blocks
        for block_num, lines in block_lines.items():
            if not lines:
                continue

            # Calculate block bounding box
            min_x = min(line.bounding_box.x for line in lines)
            min_y = min(line.bounding_box.y for line in lines)
            max_x = max(line.bounding_box.x2 for line in lines)
            max_y = max(line.bounding_box.y2 for line in lines)

            block_bbox = BoundingBox(
                x=min_x,
                y=min_y,
                width=max_x - min_x,
                height=max_y - min_y
            )

            # Calculate average confidence for block
            block_conf = sum(line.confidence for line in lines) / len(lines)

            # Concatenate text
            block_text = '\n'.join(line.text for line in lines)

            block = OcrBlock(
                text=block_text,
                lines=lines,
                confidence=block_conf,
                bounding_box=block_bbox
            )
            blocks.append(block)

        return all_words, blocks

    def draw_bounding_boxes_from_base64(
            self,
            base64_encoded_image: str,
            ocr_result: OcrResult,
            draw_level: Literal['words', 'lines', 'blocks'] = 'words',
            box_color: str = 'red',
            show_confidence: bool = True
    ) -> str:
        """
        Draw bounding boxes on a base64 encoded image and return annotated image as base64

        Args:
            base64_encoded_image: Base64 encoded image string
            ocr_result: OcrResult with bounding boxes to draw
            draw_level: Level to draw ('words', 'lines', or 'blocks')
            box_color: Color of bounding boxes (e.g., 'red', 'green', '#FF0000')
            show_confidence: Whether to show confidence scores on boxes

        Returns:
            Base64 encoded annotated image string with data URI prefix
        """
        try:
            # Remove data URI prefix if present
            image_format = 'jpeg'  # default
            if base64_encoded_image.startswith(DATA_URI_PREFIX):
                parts = base64_encoded_image.split(',', 1)
                # Extract format from data URI (e.g., data:image/png;base64,...)
                if 'image/' in parts[0]:
                    image_format = parts[0].split('image/')[1].split(';')[0]
                base64_encoded_image = parts[1]

            # Decode base64 to bytes
            image_bytes = base64.b64decode(base64_encoded_image)

            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            # Draw bounding boxes
            annotated_image = self._draw_boxes_on_image(
                image, ocr_result, draw_level, box_color, show_confidence
            )

            # Convert back to base64
            buffer = io.BytesIO()
            annotated_image.save(buffer, format=image_format.upper())
            buffer.seek(0)
            annotated_base64 = base64.b64encode(buffer.read()).decode('utf-8')

            # Return with data URI prefix
            return f"data:image/{image_format};base64,{annotated_base64}"

        except Exception as e:
            self._logger.error(f"Failed to draw bounding boxes on base64 image: {str(e)}")
            # Return original image on error
            if not base64_encoded_image.startswith(DATA_URI_PREFIX):
                return f"data:image/jpeg;base64,{base64_encoded_image}"
            return base64_encoded_image

    def draw_bounding_boxes_from_url(
            self,
            image_url: str,
            ocr_result: OcrResult,
            draw_level: Literal['words', 'lines', 'blocks'] = 'words',
            box_color: str = 'red',
            show_confidence: bool = True
    ) -> str:
        """
        Download image from URL, draw bounding boxes, and return annotated image as base64

        Args:
            image_url: URL of the image to annotate
            ocr_result: OcrResult with bounding boxes to draw
            draw_level: Level to draw ('words', 'lines', or 'blocks')
            box_color: Color of bounding boxes (e.g., 'red', 'green', '#FF0000')
            show_confidence: Whether to show confidence scores on boxes

        Returns:
            Base64 encoded annotated image string with data URI prefix
        """
        try:
            # Download image from URL
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # Convert to PIL Image
            image = Image.open(io.BytesIO(response.content))

            # Draw bounding boxes
            annotated_image = self._draw_boxes_on_image(
                image, ocr_result, draw_level, box_color, show_confidence
            )

            # Convert to base64
            buffer = io.BytesIO()
            annotated_image.save(buffer, format='JPEG')
            buffer.seek(0)
            annotated_base64 = base64.b64encode(buffer.read()).decode('utf-8')

            # Return with data URI prefix
            return f"data:image/jpeg;base64,{annotated_base64}"

        except Exception as e:
            self._logger.error(f"Failed to draw bounding boxes on image from URL: {str(e)}")
            # Return empty data URI on error
            return "data:image/jpeg;base64,"

    def _draw_boxes_on_image(
            self,
            image: Image.Image,
            ocr_result: OcrResult,
            draw_level: Literal['words', 'lines', 'blocks'],
            box_color: str,
            show_confidence: bool
    ) -> Image.Image:
        """
        Internal method to draw bounding boxes on an image

        Args:
            image: PIL Image to annotate
            ocr_result: OcrResult with bounding boxes
            draw_level: Level to draw ('words', 'lines', or 'blocks')
            box_color: Color of bounding boxes
            show_confidence: Whether to show confidence scores

        Returns:
            Annotated PIL Image
        """
        # Create a copy to avoid modifying original
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)

        # Try to load a font, fall back to default if unavailable
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        except Exception:
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except Exception:
                font = ImageFont.load_default()

        # Draw based on selected level
        if draw_level == 'words':
            for word in ocr_result.words:
                self._draw_single_box(
                    draw, word.bounding_box, word.confidence if show_confidence else None,
                    box_color, font
                )

        elif draw_level == 'lines':
            for block in ocr_result.blocks:
                for line in block.lines:
                    self._draw_single_box(
                        draw, line.bounding_box, line.confidence if show_confidence else None,
                        box_color, font
                    )

        elif draw_level == 'blocks':
            for block in ocr_result.blocks:
                self._draw_single_box(
                    draw, block.bounding_box, block.confidence if show_confidence else None,
                    box_color, font
                )

        return annotated

    def _draw_single_box(
            self,
            draw: ImageDraw.ImageDraw,
            bbox: BoundingBox,
            confidence: Optional[float],
            color: str,
            font: ImageFont.ImageFont
    ) -> None:
        """
        Draw a single bounding box with optional confidence label

        Args:
            draw: ImageDraw object
            bbox: Bounding box to draw
            confidence: Optional confidence score to display
            color: Box color
            font: Font for text labels
        """
        # Draw rectangle
        draw.rectangle(
            [(bbox.x, bbox.y), (bbox.x2, bbox.y2)],
            outline=color,
            width=2
        )

        # Draw confidence label if provided
        if confidence is not None:
            label = f"{confidence:.1f}%"
            # Position label above box
            label_y = max(0, bbox.y - 15)

            # Draw text background for readability
            try:
                # For newer Pillow versions with textbbox
                text_bbox = draw.textbbox((bbox.x, label_y), label, font=font)
                draw.rectangle(text_bbox, fill='white')
            except AttributeError:
                # Fallback for older Pillow versions
                pass

            draw.text((bbox.x, label_y), label, fill=color, font=font)