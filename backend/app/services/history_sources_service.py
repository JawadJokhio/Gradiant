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
You are an image relevance classifier for Pakistan Studies History (Paper 1 source questions).

Rule:
- Accept ONLY images related to Pakistan/Subcontinent history from 1500 CE to present.
- Reject unrelated images (selfies, products, random notes, science/math/geography-only visuals).
- Reject history topics outside the scope when clearly non-Pakistan/Subcontinent focused.

Accept examples:
- Mughal era, decline of Mughals, British expansion in India, War of Independence 1857
- Sir Syed, Aligarh Movement, Partition of Bengal, Khilafat, Pakistan Movement, post-1947 Pakistan
- Source-based exam pages, political cartoons, historical photographs/documents in this syllabus scope

Return STRICT JSON only:
{"relevant": true/false, "reason": "short reason"}
"""
        user_prompt = (
            "Classify whether this uploaded image is relevant to Pakistan history "
            f"(1500-present). Optional user query: {query}"
        )

        def _parse_json_or_none(raw_text: str):
            if not raw_text:
                return None
            text = raw_text.strip()
            try:
                return json.loads(text)
            except Exception:
                pass

            fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, flags=re.IGNORECASE)
            if fenced:
                try:
                    return json.loads(fenced.group(1).strip())
                except Exception:
                    pass

            inline = re.search(r"(\{[\s\S]*\})", text)
            if inline:
                try:
                    return json.loads(inline.group(1).strip())
                except Exception:
                    pass
            return None

        try:
            raw = self.llm_service.generate_vision_response(system_prompt, user_prompt, image_base64)
            parsed = _parse_json_or_none(raw)
            if parsed is not None:
                return {
                    "relevant": bool(parsed.get("relevant", False)),
                    "reason": str(parsed.get("reason", "Could not verify history relevance.")).strip()
                }

            lowered = raw.lower()
            positive_tokens = [
                "pakistan", "subcontinent", "mughal", "british", "partition",
                "sir syed", "war of independence", "source", "paper 1", "history"
            ]
            negative_tokens = [
                "selfie", "product", "invoice", "math", "physics", "chemistry", "geography map"
            ]
            positive_score = sum(1 for token in positive_tokens if token in lowered)
            negative_score = sum(1 for token in negative_tokens if token in lowered)
            return {
                "relevant": positive_score > negative_score,
                "reason": "Classifier returned non-JSON output; used text fallback."
            }
        except Exception:
            return {
                "relevant": False,
                "reason": "Relevance check unavailable; refusing to avoid wrong-subject answering."
            }

    def analyze_source_image(self, image_base64: str, query: str, marks: int) -> str:
        if marks not in (3, 5):
            marks = 5

        context = self._build_dataset_context(query)
        if marks == 3:
            system_prompt = f"""
You are a Cambridge O-Level Pakistan Studies History examiner for source-based Paper 1 questions.

TASK TYPE: 3-mark source question (textual source in uploaded image)

INSTRUCTIONS:
1. Read the source text from the image and transcribe the source accurately first.
2. Rephrase the extracted source in simple student-friendly language.
3. Give EXACTLY 3 concise rephrased points from the source only.
4. Do not add outside facts unless absolutely needed for one-line clarification.
5. Keep response focused and exam-ready.

USE THIS DATASET CONTEXT (for alignment with Paper 1 style):
{context}
"""
            user_prompt = (
                "The student uploaded a history source image for a 3-mark question. "
                f"Question hint from user: {query}. Extract and rephrase source text into exactly 3 points."
            )
        else:
            system_prompt = f"""
You are a Cambridge O-Level Pakistan Studies History examiner for source-based Paper 1 questions.

TASK TYPE: 5-mark source question (image + question analysis)

INSTRUCTIONS:
1. Identify the asked question from the image/query.
2. Analyze the source image content carefully (people, text, symbols, historical cues, tone, purpose).
3. Provide EXACTLY 5 relevant, mark-worthy points linked to the asked question.
4. Keep each point specific and evidence-led from what is visible in the source.
5. If required, use historical background knowledge briefly, but prioritize visual/source evidence.

USE THIS DATASET CONTEXT (for alignment with Paper 1 style):
{context}
"""
            user_prompt = (
                "The student uploaded a history source image for a 5-mark question. "
                f"Question hint from user: {query}. Provide exactly 5 relevant points from the source."
            )

        return self.llm_service.generate_vision_response(system_prompt, user_prompt, image_base64)
