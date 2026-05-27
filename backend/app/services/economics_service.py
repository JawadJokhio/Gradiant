"""
Economics MCQ Service
Handles text and image-based MCQ explanation for Cambridge O-Level Economics (2281).
"""

import json
import re
import os
from app.services.llm_service import LLMService
from app.utils.nlp_utils import nlp_processor

llm = LLMService()

# Load dataset
DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "economics", "economics_dataset.json")

def _load_dataset() -> dict:
    try:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

ECON_DATASET = _load_dataset()

# ── System Prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert Cambridge O-Level Economics MCQ Examiner (Syllabus 2281).
Your task is to explain a single MCQ question worth 1 mark.

ALWAYS return ONLY valid JSON in exactly this shape:
{
  "correct_option": "A/B/C/D or the correct answer text",
  "rationale": "2-3 sentences explaining WHY this option is correct using economic theory.",
  "why_others_wrong": "1 sentence each for why the 3 incorrect options are wrong.",
  "concept": "The specific economics concept being tested (e.g. 'Price Elasticity of Demand').",
  "examiner_tip": "A concise tip to avoid common traps for this type of MCQ.",
  "difficulty": "Easy / Medium / Hard"
}

RULES:
1. Return ONLY valid JSON. No text outside JSON.
2. Be precise — MCQs test exact definitions and logical chains.
3. Ground your answer in Cambridge 2281 syllabus coverage.
4. 'why_others_wrong' must address each distractor individually.
"""

def _extract_json(raw: str) -> dict:
    """Safely extract JSON from LLM response."""
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {"correct_option": "Unable to parse", "rationale": raw, "why_others_wrong": "", "concept": "", "examiner_tip": "", "difficulty": "Unknown"}


def _get_context(query: str) -> str:
    """Find relevant examiner tips and topic context from the dataset."""
    context_parts = []
    processed = set(nlp_processor.preprocess(query))

    topics = ECON_DATASET.get("topics", {})
    matched_traps = []
    matched_defs = []

    for topic_data in topics.values():
        keywords = set(topic_data.get("keywords", []))
        if processed.intersection(keywords):
            matched_traps.extend(topic_data.get("mcq_traps", [])[:2])
            key_defs = topic_data.get("key_definitions", {})
            for key, val in key_defs.items():
                if key.replace("_", " ") in query.lower():
                    matched_defs.append(f"- **{key.replace('_', ' ').title()}**: {val}")

    if matched_traps:
        context_parts.append("### Common MCQ Traps for this topic:\n" + "\n".join(f"- {t}" for t in matched_traps[:3]))
    if matched_defs:
        context_parts.append("### Relevant Definitions:\n" + "\n".join(matched_defs[:3]))

    general_tips = ECON_DATASET.get("exam_tips", [])
    if general_tips:
        context_parts.append("### General Examiner Tips:\n" + "\n".join(f"- {t}" for t in general_tips[:3]))

    return "\n\n".join(context_parts)


def explain_mcq_text(query: str) -> dict:
    """Explain an economics MCQ provided as text."""
    context = _get_context(query)
    prompt = f"{SYSTEM_PROMPT}\n\n### SYLLABUS CONTEXT:\n{context}"
    user_msg = f"Explain this MCQ:\n{query}"

    raw = llm.generate_response(prompt, user_msg)
    return _extract_json(raw)


def explain_mcq_image(image_base64: str, query: str = "") -> dict:
    """Explain an economics MCQ from an uploaded image using vision AI."""
    context = _get_context(query)
    system = f"{SYSTEM_PROMPT}\n\n### SYLLABUS CONTEXT:\n{context}"
    user_msg = (
        "Read ALL text from the image carefully — including the question stem, all 4 options, "
        "and any data/diagrams provided. Then explain the MCQ fully."
    )
    if query:
        user_msg += f"\n\nAdditional context from user: {query}"

    raw = llm.generate_vision_response(system, user_msg, image_base64)
    return _extract_json(raw)
