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
    marks: int = Form(4),
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

    ===== STRICT SUBJECT RELEVANCE (CRITICAL) =====
    If the question is NOT related to O-Level Pakistan Studies Geography or the geography/economy of Pakistan, you MUST REFUSE to answer.
    Do NOT answer general knowledge, history, science, or geography of other unrelated countries unless directly impacting Pakistan.
    If refusing, ignore all other format rules below. Reply EXACTLY with: "I am a dedicated Cambridge O-Level Pakistan Studies Geography Examiner. This question is outside my syllabus area, so I cannot answer it."
    
    Provide an expert geographical breakdown for: "{query}" in the context of Pakistan, calibrated for a {marks}-mark answer.
    
    ===== GEOGRAPHICAL KNOWLEDGE BASE =====
    {knowledge_context}
    ========================================

    Format your response with:
    [1] Curriculum Context
    [Brief overview]
    
    [2] Distribution Analysis
    [Where these are found and WHY - physical factors like relief, soil, climate]
    
    [3] Economic Significance
    [Impact on Pakistan's GDP, trade, or local livelihoods]
    
    [4] Tutor Wisdom
    [One-sentence exam tip]
    
    Use technical terms (Relief, Alluvial, Rabi/Kharif, Perennial).
    Depth: Approximately {marks * 25} words.

    ===== POPUP ENHANCEMENT (STRICT FORMAT) =====
    For each entity name mentioned in the knowledge base, generate exactly 2 short bullet points for the O-Level curriculum.
    At the VERY END of your response, add a section starting with '---POPUP_DATA---' and list them as 'Entity Name: Point 1; Point 2'.
    """

    raw_response = llm_service.generate_response(system_prompt, query)
    
    # Parse Popup Data
    explanation = raw_response
    popup_mapping = {}
    
    if "---POPUP_DATA---" in raw_response:
        parts = raw_response.split("---POPUP_DATA---")
        explanation = parts[0].strip()
        popup_section = parts[1].strip()
        
        for line in popup_section.split("\n"):
            if ":" in line:
                name, points = line.split(":", 1)
                popup_mapping[name.strip().lower()] = points.strip()

    # Inject AI points into features
    for feature in features:
        label = feature.get("label", "").lower()
        if label in popup_mapping:
            feature["facts"] = popup_mapping[label]

    return MapAnalysisResponse(
        features=features,
        explanation=explanation,
        query=query
    )
