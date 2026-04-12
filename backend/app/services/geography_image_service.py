from app.services.llm_service import LLMService

class GeographyImageAnalysisService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def extract_graph_context(self, image_base64: str, query: str = "") -> str:
        """Extracts the question, visual data and all labels from the image."""
        system_prompt = """
        You are a Cambridge O-Level Past Paper Reader.
        Carefully analyze this image and extract ALL of the following:
        1. TRANSCRIBE any written/printed question(s) EXACTLY as they appear - word for word.
        2. Identify what type of figure is shown (map, bar chart, pie chart, line graph, diagram).
        3. List ALL labels, place names, letters (like W, X, Y, Z), river names, keys/legends shown on the figure.
        4. Note any axis labels, scale bars, compass directions, or statistical values.
        Be extremely precise. Do NOT attempt to answer the question - only extract.
        """        
        user_prompt = f"Transcribe the question(s) and extract all data from this image. User query (optional context): {query}"
        
        try:
            return self.llm_service.generate_vision_response(system_prompt, user_prompt, image_base64)
        except Exception as e:
            return f"Error extracting image details: {str(e)}"

    def evaluate_image_answer(self, image_context: str, query: str, context_string: str, marks: int) -> str:
        """Answer the specific question found in the image using extracted data + RAG knowledge."""
        system_prompt = f"""
        You are a Cambridge O-Level Geography Examiner (Syllabus 2217).
        A student has uploaded an image of a past paper question.

        ===== EXTRACTED IMAGE CONTENT (question + figure data) =====
        {image_context}
        ============================================================

        ===== ADDITIONAL GEOGRAPHICAL KNOWLEDGE BASE =====
        {context_string}
        ==================================================

        INSTRUCTIONS:
        - Identify the EXACT question(s) from the extracted image content above.
        - Answer EACH question part directly and specifically (e.g. if asked "Name rivers W and X", give the actual river names).
        - Use ONLY the information visible in the figure/image for questions that say "Using Fig. X only".
        - For other questions, supplement with your geographical knowledge.
        - Award yourself {marks} marks: provide exactly {marks} distinct, mark-worthy points.
        - Format clearly: use bold question parts (e.g. **(i)**, **(ii)**) before each answer.
        - End with a brief **Tutor Wisdom** tip relevant to the question type.
        """
        user_prompt = f"Answer all question parts found in the image. User note: {query}"

        return self.llm_service.generate_response(system_prompt, user_prompt)
