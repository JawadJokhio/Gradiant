from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.core.dependencies import get_geography_service, get_llm_service
from app.services.geography_service import GeographyService
from app.services.llm_service import LLMService
from app.models.schemas import MapAnalysisResponse
from typing import Optional

router = APIRouter(tags=["Geography Map Analysis"])

@router.post("/geography/analyze-map", response_model=MapAnalysisResponse)
async def analyze_geography_map(
    query: str = Form(...),
    image: Optional[UploadFile] = File(None),
    geography_service: GeographyService = Depends(get_geography_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    query_lower = query.lower()
    
    category = geography_service.detect_category(query_lower)
    entity_matches = geography_service.match_entities(query_lower)

    features = []
    matched_facts = []

    if entity_matches:
        top_matches = entity_matches[:10]
        for _, cat, item in top_matches:
            matched_facts.append(f"{item.get('name')}: {item.get('facts', '')}")
            features.extend(geography_service.convert_to_feature(cat, item))

    elif category:
        geography_data = geography_service.data_repository.get_geography_data()
        items = geography_data.get(category, [])

        if isinstance(items, dict):
            items = [i for sub in items.values() for i in sub]

        for item in items[:10]:
            matched_facts.append(f"{item.get('name')}: {item.get('facts', '')}")
            features.extend(geography_service.convert_to_feature(category, item))

    else:
        matched_facts.append("No strong geographical match found.")

    knowledge_context = "\n".join(matched_facts[:10]) 
    
    system_prompt = f"""
    You are the Cambridge Geography Examiner (Syllabus 2217/02).
    Provide an expert geographical breakdown for: "{query}" in the context of Pakistan.
    
    ===== GEOGRAPHICAL KNOWLEDGE BASE =====
    {knowledge_context}
    ========================================

    Format your response with:
    ### [1] Curriculum Context
    [Brief overview]
    
    ### [2] Distribution Analysis
    [Where these are found and WHY - physical factors like relief, soil, climate]
    
    ### [3] Economic Significance
    [Impact on Pakistan's GDP, trade, or local livelihoods]
    
    ### [4] Tutor Wisdom
    [One-sentence exam tip]
    
    Use technical terms (Relief, Alluvial, Rabi/Kharif, Perennial).
    Keep it concise (~100 words).
    """

    explanation = llm_service.generate_response(system_prompt, query)

    return MapAnalysisResponse(
        features=features,
        explanation=explanation,
        query=query
    )
