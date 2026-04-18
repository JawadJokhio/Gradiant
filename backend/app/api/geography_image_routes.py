from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.core.dependencies import get_geography_image_analysis_service, get_geography_service
from app.services.geography_image_service import GeographyImageAnalysisService
from app.services.geography_service import GeographyService
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
    geography_service: GeographyService = Depends(get_geography_service)
):
    try:
        content = await image.read()
        base64_img = extract_base64_from_file(content)
    except Exception as e:
        raise InvalidImageException(f"Failed to read image: {str(e)}")

    if not query or query.strip() == "":
        query = "If the image contains a specific past-paper question, answer it comprehensively. Otherwise, provide a detailed geographical analysis of the map, graph, diagram, or data shown."

    # 1. Perform a quick extraction to get keywords for RAG context
    # This helps even if the user query is vague (e.g. "Analyze this")
    image_context = geography_image_analysis_service.extract_graph_context(base64_img, query)

    # 2. Get Geographic RAG context using both user query and image context
    search_query = f"{query} {image_context}"
    entity_matches = geography_service.match_entities(search_query)
    
    matched_facts = []
    if entity_matches:
        for _, cat, item in entity_matches[:5]:
             matched_facts.append(f"{item.get('name')}: {item.get('facts', '')}")
    
    geo_context_text = "\n".join(matched_facts)
    if not geo_context_text:
        geo_context_text = "No additional geographic background context found."

    # 3. Direct Vision-to-Answer Analysis
    # The vision model looks at the image and the context to provide the final answer
    answer = geography_image_analysis_service.analyze_geography_image_direct(
        image_base64=base64_img,
        query=query,
        context_string=geo_context_text,
        marks=marks
    )

    return AIAnswerResponse(answer=answer, marks=marks)
