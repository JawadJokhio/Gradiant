from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.core.dependencies import get_geography_image_analysis_service, get_geography_service, get_llm_service
from app.services.geography_image_service import GeographyImageAnalysisService
from app.services.geography_service import GeographyService
from app.services.llm_service import LLMService
from app.services.ocr_service import OCRService
from app.models.schemas import AIAnswerResponse
from app.core.exceptions import InvalidImageException
from app.utils.helpers import extract_base64_from_file

router = APIRouter(tags=["Geography Image Analysis"])

@router.post("/geography/analyze-image-question", response_model=AIAnswerResponse)
async def analyze_geography_image_question(
    image: UploadFile = File(...),
    query: str = Form(""),
    marks: int = Form(4),
    geography_image_analysis_service: GeographyImageAnalysisService = Depends(get_geography_image_analysis_service),
    geography_service: GeographyService = Depends(get_geography_service),
    llm_service: LLMService = Depends(get_llm_service),
):
    try:
        content = await image.read()
        base64_img = extract_base64_from_file(content)
    except Exception as e:
        raise InvalidImageException(f"Failed to read image: {str(e)}")

    if not query or query.strip() == "":
        query = "If the image contains a specific past-paper question, answer it comprehensively. Otherwise, provide a detailed geographical analysis of the map, graph, diagram, or data shown."

    # ── Step 0: OCR pre-pass ─────────────────────────────────────────────────
    # Extract printed text from the image before calling the vision model.
    # Enriches RAG query and reduces expensive vision API calls.
    ocr_text = ""
    try:
        ocr_svc = OCRService(llm_service=llm_service)
        ocr_result = ocr_svc.extract_text_from_base64(base64_img, mode="printed")
        if ocr_result.confidence > 0.3 and ocr_result.raw_text.strip():
            ocr_text = ocr_result.raw_text.strip()
    except Exception:
        pass  # OCR failure is non-blocking

    # Hard relevance gate: only geography-related images are allowed for answering.
    relevance = geography_image_analysis_service.check_geography_image_relevance(base64_img, query)
    if not relevance.get("relevant", False):
        return AIAnswerResponse(
            answer=(
                f"Uploaded image geography se relevant nahi lag rahi. "
                f"Reason: {relevance.get('reason', 'Not geography-related image.')} "
                "Please geography map, graph, diagram ya past-paper figure upload karein."
            ),
            marks=marks
        )

    # 1. Quick extraction to get keywords for RAG context.
    #    Inject OCR text so the vision model gets a head-start on labels/questions.
    ocr_hint = f"\n\n[PRE-EXTRACTED TEXT VIA OCR]:\n{ocr_text}" if ocr_text else ""
    image_context = geography_image_analysis_service.extract_graph_context(
        base64_img, f"{query}{ocr_hint}"
    )

    # 2. Get Geographic RAG context using user query + OCR text + image context
    search_query = f"{query} {ocr_text} {image_context}"
    entity_matches = geography_service.match_entities(search_query)

    matched_facts = []
    if entity_matches:
        for _, cat, item in entity_matches[:5]:
            matched_facts.append(f"{item.get('name')}: {item.get('facts', '')}")

    geo_context_text = "\n".join(matched_facts)
    if not geo_context_text:
        geo_context_text = "No additional geographic background context found."

    # 3. Direct Vision-to-Answer Analysis
    answer = geography_image_analysis_service.analyze_geography_image_direct(
        image_base64=base64_img,
        query=query,
        context_string=geo_context_text,
        marks=marks
    )

    return AIAnswerResponse(answer=answer, marks=marks)
