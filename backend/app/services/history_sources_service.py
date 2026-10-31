import json
import re
from typing import List

from app.repositories.data_repository import DataRepository
from app.services.llm_service import LLMService


class HistorySourcesService:
    def __init__(self, llm_service: LLMService, data_repository: DataRepository):
        self.llm_service = llm_service
        self.data_repository = data_repository

    def _build_dataset_context(self, user_query: str) -> str:
        data = self.data_repository.get_history_sources_data()
        entries = data.get("entries", [])
        if not entries:
            return "No source-based past-paper dataset context available."

        keywords = set(re.findall(r"\w+", user_query.lower()))
        ranked: List[tuple[int, dict]] = []
        for entry in entries:
            question = entry.get("question", "")
            tokens = set(re.findall(r"\w+", question.lower()))
            score = len(tokens.intersection(keywords))
            if score > 0:
                ranked.append((score, entry))

        ranked.sort(key=lambda x: x[0], reverse=True)
        selected = [entry for _, entry in ranked[:5]]
        if not selected:
            selected = entries[:3]

        lines = []
        for item in selected:
            lines.append(f"- Year: {item.get('year', '')}, Session: {item.get('session', '')}, Paper: {item.get('paper', '')}")
            lines.append(f"  Question: {item.get('question', '')}")
            for point in item.get("mark_scheme_points", [])[:5]:
                lines.append(f"  • {point}")
        return "\n".join(lines)

    def check_history_image_relevance(self, image_base64: str, query: str = "") -> dict:
        """
        Validate image relevance for Pakistan history (1500-present).
        Returns: {"relevant": bool, "reason": str}
        """
        system_prompt = """
You are an image relevance classifier for Cambridge O-Level Pakistan Studies History (Paper 1, Syllabus 2059/01).
Decide whether the image contains content related to O-Level Pakistan Studies History (1500 CE to present).

Relevant examples:
- Historical text sources mentioning events or personalities (Mughals, British, 1857 War, Sir Syed, Partition, Khilafat, Jinnah, Iqbal, etc.)
- Historical political cartoons, maps, or photographs of leaders/events
- Past paper questions, mark schemes, worksheets, or student answer sheets for Paper 1 (2059/01)
- Book pages, notes, or source extracts about Subcontinent history

Not relevant examples:
- Selfies, random personal photos, memes, products, pets
- Math or science question papers with no history content
- Images completely unrelated to education or history

IMPORTANT:
- If uncertain or if the image appears to be an exam or study document, prefer relevant (true).
- Return STRICT JSON ONLY:
{"relevant": true/false, "reason": "brief reason"}
"""
        user_prompt = f"Classify image relevance for O-Level History. User context / query: {query}"

        def _parse_json_or_none(raw_text: str):
            if not raw_text:
                return None
            text = raw_text.strip()
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
            patterns = [
                r"```(?:json)?\s*(\{[\s\S]*?\})\s*```",
                r"(\{[\s\S]*\})"
            ]
            for pattern in patterns:
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if match:
                    try:
                        return json.loads(match.group(1).strip())
                    except json.JSONDecodeError:
                        continue
            return None

        # Check user query / extracted OCR text first
        query_lower = (query or "").lower()
        history_tokens = [
            "history", "pakistan", "2059", "source", "mughal", "british", "east india",
            "1857", "war of independence", "sir syed", "aligarh", "partition", "bengal",
            "khilafat", "allama iqbal", "iqbal", "jinnah", "quaid", "past paper", "paper 1",
            "plassey", "clive", "congress", "muslim league", "simla", "lahore resolution",
            "cabinet mission", "radcliffe", "1940", "1947", "ayub", "bhutto", "zia", "kashmir",
            "tipu", "maratha", "aurangzeb", "greased", "cartridge", "doctrine of lapse", "annexation",
            "swadeshi", "curzon", "minto", "morley", "lucknow", "rowlatt", "amritsar", "jallianwala"
        ]
        if any(tok in query_lower for tok in history_tokens):
            return {
                "relevant": True,
                "reason": "User query / extracted source confirmed historical context."
            }

        try:
            raw = self.llm_service.generate_vision_response(system_prompt, user_prompt, image_base64)
            parsed = _parse_json_or_none(raw)
            if parsed is not None:
                return {
                    "relevant": bool(parsed.get("relevant", False)),
                    "reason": str(parsed.get("reason", "Verified historical content.")).strip()
                }

            raw_lower = (raw or "").lower()
            if "vision engines offline" in raw_lower or "runtime failed" in raw_lower or "error" in raw_lower:
                return {
                    "relevant": True,
                    "reason": "Vision check unavailable; proceeding with source analysis."
                }

            positive_score = sum(1 for token in history_tokens if token in raw_lower)
            negative_tokens = ["selfie", "meme", "pet", "product", "advertisement", "invoice", "math equation"]
            negative_score = sum(1 for token in negative_tokens if token in raw_lower)

            return {
                "relevant": positive_score >= negative_score,
                "reason": "Matched historical syllabus vocabulary."
            }
        except Exception:
            # Tolerant fallback: never block an exam student if the classifier encounters a transient issue
            return {
                "relevant": True,
                "reason": "Classifier fallback active; proceeding with analysis."
            }

    def analyze_source_image(self, image_base64: str, query: str, marks: int) -> str:
        if marks not in (3, 5):
            marks = 5

        context = self._build_dataset_context(query)
        if marks == 3:
            system_prompt = f"""
You are a Cambridge O-Level Pakistan Studies History examiner. 

TASK TYPE: 3-mark source question

CRITICAL INSTRUCTIONS:
1. Read the source text from the uploaded image.
2. COMPLETELY IGNORE whether the user's question perfectly matches the source's exact vocabulary. (e.g. if the user asks about "Mughal rule" but the source is about "Robert Clive and Nawab Siraj-ud-Daula", treat them as historically connected).
3. DO NOT evaluate the user's question. DO NOT ever say "The source does not mention...". 
4. Your ONLY task is to extract the main facts actually written in the source and rewrite them into a single, direct, factual paragraph.
5. NO introductory sentences (like "The source states that"). NO bullet points. NO excuses. Just the facts from the source rephrased.
6. The answer MUST be strictly between 40 to 80 words.
7. Use simple, easy-to-understand English suitable for a high school student.

USE THIS DATASET CONTEXT (for alignment with Paper 1 style):
{context}
"""
            user_prompt = (
                "The student uploaded a history source image for a 3-mark question. "
                f"Question hint from user: {query}. Extract and summarize the source's contents in a direct 40-80 word paragraph. DO NOT make excuses about missing information."
            )
        else:
            system_prompt = f"""
You are a Cambridge O-Level Pakistan Studies History examiner for source-based Paper 1 questions.

TASK TYPE: 5-mark source question (image + question analysis)

CRITICAL INSTRUCTIONS:
1. Analyze the source image content carefully (people, text, symbols, historical cues, tone, purpose).
2. Provide EXACTLY 5 relevant, mark-worthy bullet points linked to the asked question.
3. Keep each point specific and evidence-led from what is visible in the source.
4. DO NOT output any headers, steps, introductions, or conclusions (e.g., no "Step 1", no "Conclusion").
5. Output ONLY the 5 bullet points directly.
6. Use simple, easy-to-understand English suitable for a high school student.

USE THIS DATASET CONTEXT (for alignment with Paper 1 style):
{context}
"""
            user_prompt = (
                "The student uploaded a history source image for a 5-mark question. "
                f"Question hint from user: {query}. Provide exactly 5 relevant bullet points directly, with no extra text, steps, or conclusions."
            )

        return self.llm_service.generate_vision_response(system_prompt, user_prompt, image_base64)
