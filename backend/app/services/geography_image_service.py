import json
from app.services.llm_service import LLMService

class GeographyImageAnalysisService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def extract_graph_context(self, image_base64: str, query: str = "") -> str:
        """Extracts the question, visual data and all labels from the image."""
        system_prompt = """
        You are a Cambridge O-Level Past Paper Reader specializing in Geography (2217).
        Carefully analyze this image and extract ALL of the following in a clear, labeled format:

        1. QUESTIONS: Transcribe every question/sub-question EXACTLY as written. 
           IMPORTANT: Include the marks assigned to each question (e.g., [2] or 3 marks) if visible.
        
        2. FIGURE TYPE: Identify if it's a map (topographic, thematic, sketch), graph (bar, line, pie), diagram, or photograph.
        
        3. SPATIAL DATA & LABELS: 
           - List ALL labels, place names, and identifiers (W, X, Y, Z).
           - For identifiers like 'X' or 'Y' on a map, describe their EXACT location relative to other features 
             (e.g., "X is located on the bank of the river in the north-east", "Y is near the boundary of the forested area").
        
        4. LEGEND & SCALE: Extract all key/legend entries, scale bars, and north-arrows.
        
        5. STATISTICAL VALUES: List any data points or axis values shown.

        Be extremely precise. Do NOT answer the questions. Focus on providing a complete 'environmental scan' of the document.
        """        
        user_prompt = f"Transcribe the question(s) and extract all data from this image. User query (optional context): {query}"
        
        try:
            return self.llm_service.generate_vision_response(system_prompt, user_prompt, image_base64)
        except Exception as e:
            return f"Error extracting image details: {str(e)}"

    def check_geography_image_relevance(self, image_base64: str, query: str = "") -> dict:
        """Validate that uploaded image is genuinely geography/map-related before answering."""
        system_prompt = """
        You are an image relevance classifier for a Pakistan Geography Tutor app.
        Decide whether the image is relevant to geography learning tasks.

        Relevant examples:
        - Maps (physical, political, thematic, topographic)
        - Graphs/charts/diagrams related to climate, population, economy, land use, transport, rivers
        - Geography past-paper question pages or figures
        - Satellite or landscape photos clearly tied to geographical analysis

        Not relevant examples:
        - Selfies, random people photos, memes, products, pets
        - Unrelated text documents with no geography context
        - Any image where geography relevance is unclear

        Return STRICT JSON ONLY:
        {"relevant": true/false, "reason": "short reason"}
        """
        user_prompt = f"Classify image relevance. Optional user query: {query}"

        try:
            raw = self.llm_service.generate_vision_response(system_prompt, user_prompt, image_base64)
            parsed = json.loads(raw.strip())
            return {
                "relevant": bool(parsed.get("relevant", False)),
                "reason": str(parsed.get("reason", "Could not verify geography relevance.")).strip()
            }
        except Exception:
            # Safe fallback: reject if classifier output is invalid/unreliable.
            return {
                "relevant": False,
                "reason": "Could not confidently verify this image as geography-related."
            }

    def evaluate_image_answer(self, image_context: str, query: str, context_string: str, marks: int) -> str:
        """Answer the specific question found in the image using extracted data + RAG knowledge."""
        system_prompt = f"""
        You are a Cambridge O-Level Geography Examiner (Syllabus 2217).
        A student has uploaded an image of a past paper question.

        ===== EXTRACTED IMAGE CONTENT (question + figure data + spatial context) =====
        {image_context}
        ============================================================

        ===== ADDITIONAL GEOGRAPHICAL KNOWLEDGE BASE =====
        {context_string}
        ==================================================

        INSTRUCTIONS:
        1. Identify the EXACT question parts and their assigned MARKS from the extracted content.
        2. Use the extraction's spatial data (descriptions of where X and Y are) to accurately answer location-based questions.
        3. If MARKS are identified from the image for a part (e.g., [3]), provide exactly that many distinct, mark-worthy points.
        4. If NO marks are visible in the image for a part, default to providing {marks} mark-worthy points.
        5. For "Using Fig. X only" questions, restrict yourself STRICTLY to the extracted figure data.
        6. Format clearly: use bold question parts (e.g. **(i)**, **(ii)**) and bullet points for multiple marks.
        7. End with a brief **Tutor Wisdom** tip relevant to the question type.
        """
        user_prompt = f"Answer all question parts found in the image. User note: {query}"

        return self.llm_service.generate_response(system_prompt, user_prompt)

    def analyze_geography_image_direct(self, image_base64: str, query: str, context_string: str, marks: int) -> str:
        """Single-pass Vision Reasoning: Analyzes the image and answers directly in one step."""
        system_prompt = f"""
        You are a Cambridge O-Level Geography Examiner (Syllabus 2217).
        Look at the provided image (Map/Graph/Diagram) and answer the user's question directly.
        
        ===== IMPORTANT GEOGRAPHICAL CONTEXT (RAG) =====
        {context_string}
        ================================================
        
        EXAMINER RULES:
        1. SPATIAL ACCURACY: Identify markers like X, Y, W, Z by looking at their EXACT location on the map. 
           - Look for nearby features (rivers, settlements, boundaries, mountains) to determine what they represent.
        2. MARK ENFORCEMENT: Identify the marks for the question from the image (e.g. [2]). 
           - Provide EXACTLY that many distinct points. If marks are not visible, provide {marks} points.
        3. SOURCE CONTROL: If the question says "Using Fig. X only", use ONLY details visible in the image.
        4. FORMATTING: Use bold sub-parts (e.g. (i), (ii)) and bullet points.
        5. TUTOR WISDOM: End with a "Tutor Wisdom" advice based on common examiner report pitfalls for this topic.
        """
        user_prompt = f"Analyze the image and answer this question/request: {query}"
        
        try:
            return self.llm_service.generate_vision_response(system_prompt, user_prompt, image_base64)
        except Exception as e:
            return f"Error in direct vision analysis: {str(e)}"
