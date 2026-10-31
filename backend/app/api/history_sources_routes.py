from fastapi import APIRouter, UploadFile, File, Form, Depends

from app.core.dependencies import get_history_sources_service, get_llm_service
from app.core.exceptions import InvalidImageException
from app.models.schemas import AIAnswerResponse
from app.services.history_sources_service import HistorySourcesService
from app.services.llm_service import LLMService
from app.services.ocr_service import OCRService
from app.utils.helpers import extract_base64_from_file

router = APIRouter(tags=["History Sources"])


@router.post("/history-sources/analyze-image-question", response_model=AIAnswerResponse)
async def analyze_history_sources_image_question(
    image: UploadFile = File(...),
    query: str = Form(""),
    marks: int = Form(5),
    history_sources_service: HistorySourcesService = Depends(get_history_sources_service),
    llm_service: LLMService = Depends(get_llm_service),
):
    try:
        content = await image.read()
        base64_img = extract_base64_from_file(content)
    except Exception as e:
        raise InvalidImageException(f"Failed to read image: {str(e)}")

    if marks not in (3, 5):
        marks = 5

    # OCR pre-pass: extract historical text/source from image
    ocr_text = ""
    try:
        ocr_svc = OCRService(llm_service=llm_service)
        ocr_res = ocr_svc.extract_text_from_base64(base64_img, mode="printed")
        if ocr_res.confidence > 0.3 and ocr_res.raw_text.strip():
            ocr_text = ocr_res.raw_text.strip()
    except Exception:
        pass

    combined_context = f"{query}\n\n[EXTRACTED SOURCE TEXT VIA OCR]:\n{ocr_text}".strip() if ocr_text else query

    relevance = history_sources_service.check_history_image_relevance(base64_img, combined_context)
    if not relevance.get("relevant", False):
        return AIAnswerResponse(
            answer=(
                "I cannot answer this image because it does not appear to be a Pakistan History source "
                "(1500-present). "
                f"Reason: {relevance.get('reason', 'Not relevant to Pakistan history scope.')} "
                "Please upload a source/question image from Pakistan Studies History Paper 1."
            ),
            marks=marks
        )

    answer = history_sources_service.analyze_source_image(
        image_base64=base64_img,
        query=combined_context,
        marks=marks
    )
    return AIAnswerResponse(answer=answer, marks=marks)
