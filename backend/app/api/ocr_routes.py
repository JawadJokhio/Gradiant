"""
ocr_routes.py
POST /api/ocr/extract  — Extract text from an uploaded image
"""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.dependencies import get_llm_service
from app.models.schemas import OCRResult
from app.services.llm_service import LLMService
from app.services.ocr_service import OCRService
from app.utils.helpers import extract_base64_from_file

router = APIRouter(prefix="/api/ocr", tags=["OCR"])


def get_ocr_service(
    llm_service: LLMService = Depends(get_llm_service),
) -> OCRService:
    return OCRService(llm_service=llm_service)


@router.post("/extract", response_model=OCRResult)
async def extract_text_from_image(
    image: UploadFile = File(...),
    mode: str = Form("auto"),   # "printed" | "handwriting" | "math" | "auto"
    ocr_service: OCRService = Depends(get_ocr_service),
):
    """
    Extract text from an uploaded image using the multi-tier OCR pipeline.

    Modes:
    - auto      → EasyOCR (bilingual EN/UR) with Tesseract + Gemini fallback
    - printed   → Same as auto; optimised for Cambridge exam paper scans
    - handwriting → Skips directly to Gemini Vision for best accuracy
    - math      → EasyOCR pass; caller should treat output as raw equation text
    """
    try:
        content = await image.read()
        base64_img = extract_base64_from_file(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read image: {e}")

    try:
        result = ocr_service.extract_text_from_base64(base64_img, mode=mode)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {e}")

