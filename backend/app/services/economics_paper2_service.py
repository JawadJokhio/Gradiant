"""
Economics Paper 2 Service
Handles structured Cambridge O-Level Economics (2281) Paper 2 answers.
"""

import json
import os
import re
from app.services.llm_service import LLMService
from app.utils.nlp_utils import nlp_processor

llm = LLMService()

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "economics", "economics_dataset.json")


def _load_dataset() -> dict:
    try:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


ECON_DATASET = _load_dataset()

PAPER2_SYSTEM_PROMPT = """You are an expert Cambridge O-Level Economics Paper 2 Examiner (Syllabus 2281).
Answer ONLY within Cambridge O-Level Economics syllabus boundaries.

General answer rules:
1. Use clear, student-friendly English.
2. Keep every answer tied to the command word and the marks available.
3. For 2 marks: give a precise definition or two clear points.
4. For 4 marks: give two developed explanation chains.
5. For 6 marks: analyse causes/effects with linked reasoning and examples where useful.
6. For 8 marks: discuss both sides, evaluate, and finish with a justified judgement.
7. If an image shows marks beside question parts, follow those image marks exactly.
8. If data/case material is provided, use it directly in the answer.
9. Do not invent facts outside the visible source or the O-Level syllabus.
10. If a Section A question asks to draw, sketch, label, show, or illustrate an economics diagram, include a clean examiner-style SVG diagram for that part.
11. Diagrams must be standard O-Level Economics diagrams only, such as demand/supply shifts, PPC, market failure, tax/subsidy, elasticity, costs/revenue, or externality diagrams.
12. Diagram SVG rules: use only <svg>, <line>, <path>, <text>, <circle>, <rect>, <polyline>, <polygon>, <defs>, and <marker>; no scripts, no external images, no foreignObject.
13. Every market diagram must include:
    - clear axes labelled Price and Quantity
    - original curve labels such as D1 and S1
    - new curve labels such as D2/S2 when a curve shifts
    - an arrow showing the direction of shift
    - equilibrium points E1 and E2
    - dashed guide lines to show P1/P2 and Q1/Q2
    - a short visual result, e.g. lower price and lower quantity
14. For demand and supply diagrams, demand curves slope down left-to-right and supply curves slope up left-to-right. Never draw demand as a vertical line or horizontal line.
15. Make SVG diagrams readable at 720x420 with generous margins, dark strokes, and labels that do not overlap lines.

Return ONLY valid JSON in exactly this shape:
{
  "section": "A or B",
  "input_mode": "text or image",
  "marks_source": "image marks / command word inference",
  "detected_parts": [
    {
      "part": "question part label or command word",
      "marks": 2,
      "question": "the question being answered",
      "answer": "mark-scheme aligned answer",
      "diagram_svg": "full SVG string if the question asks for a diagram, otherwise null"
    }
  ],
  "examiner_tip": "short practical tip",
  "syllabus_links": ["topic 1", "topic 2"]
}
"""


def _extract_json(raw: str, section: str, input_mode: str, marks_source: str) -> dict:
    try:
        data = json.loads(raw.strip())
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError:
                data = None
        else:
            data = None

    if isinstance(data, dict):
        data.setdefault("section", section)
        data.setdefault("input_mode", input_mode)
        data.setdefault("marks_source", marks_source)
        data.setdefault("detected_parts", [])
        data.setdefault("examiner_tip", "")
        data.setdefault("syllabus_links", [])
        return data

    return {
        "section": section,
        "input_mode": input_mode,
        "marks_source": marks_source,
        "detected_parts": [
            {
                "part": "Answer",
                "marks": None,
                "question": "",
                "answer": raw,
                "diagram_svg": None,
            }
        ],
        "examiner_tip": "",
        "syllabus_links": [],
    }


def _get_context(query: str) -> str:
    context_parts = []
    processed = set(nlp_processor.preprocess(query))

    matched_defs = []
    matched_tips = []
    for topic_name, topic_data in ECON_DATASET.get("topics", {}).items():
        keywords = set(topic_data.get("keywords", []))
        if processed.intersection(keywords):
            matched_tips.extend(topic_data.get("mcq_traps", [])[:2])
            key_defs = topic_data.get("key_definitions", {})
            for key, value in key_defs.items():
                if key.replace("_", " ") in query.lower():
                    matched_defs.append(f"- {key.replace('_', ' ').title()}: {value}")
            context_parts.append(f"- Matched topic: {topic_name}")

    if matched_defs:
        context_parts.append("Relevant definitions:\n" + "\n".join(matched_defs[:5]))
    if matched_tips:
        context_parts.append("Relevant examiner cautions:\n" + "\n".join(f"- {tip}" for tip in matched_tips[:5]))

    general_tips = ECON_DATASET.get("exam_tips", [])
    if general_tips:
        context_parts.append("General tips:\n" + "\n".join(f"- {tip}" for tip in general_tips[:4]))

    return "\n\n".join(context_parts)


def _infer_section_b_marks(query: str) -> list[dict]:
    mark_map = {
        "define": 2,
        "explain": 4,
        "analyse": 6,
        "analyze": 6,
        "discuss": 8,
    }
    pattern = re.compile(r"\b(define|explain|analyse|analyze|discuss)\b", re.IGNORECASE)
    matches = list(pattern.finditer(query))

    if not matches:
        return [{"command": "auto", "marks": None, "question": query.strip()}]

    parts = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(query)
        command = match.group(1).lower()
        parts.append({
            "command": command,
            "marks": mark_map[command],
            "question": query[start:end].strip(),
        })
    return parts


def _asks_for_diagram(text: str) -> bool:
    return bool(re.search(r"\b(draw|sketch|diagram|illustrate|show on a diagram|label)\b", text, re.IGNORECASE))


def _infer_market_shift(text: str) -> tuple[str, str] | None:
    lowered = text.lower()
    demand_terms = [
        "demand", "population", "income", "taste", "advertising", "substitute",
        "complement", "consumer", "buyers", "fashion"
    ]
    supply_terms = [
        "supply", "cost of production", "costs of production", "technology",
        "productivity", "tax", "subsidy", "raw material", "wage", "producer"
    ]
    decrease_terms = ["decrease", "fall", "falls", "fell", "decline", "lower", "fewer", "reduction", "reduced"]
    increase_terms = ["increase", "rise", "rises", "rose", "higher", "more", "growth", "grown"]

    if any(term in lowered for term in demand_terms):
        if any(term in lowered for term in decrease_terms):
            return ("demand", "decrease")
        if any(term in lowered for term in increase_terms):
            return ("demand", "increase")

    if any(term in lowered for term in supply_terms):
        if "subsidy" in lowered or "technology" in lowered or "productivity" in lowered:
            return ("supply", "increase")
        if "tax" in lowered or any(term in lowered for term in decrease_terms):
            return ("supply", "decrease")
        if any(term in lowered for term in increase_terms):
            return ("supply", "increase")

    return None


def _market_diagram_svg(shift_curve: str, direction: str) -> str:
    demand_decrease = shift_curve == "demand" and direction == "decrease"
    demand_increase = shift_curve == "demand" and direction == "increase"
    supply_decrease = shift_curve == "supply" and direction == "decrease"
    supply_increase = shift_curve == "supply" and direction == "increase"

    if demand_decrease:
        d1 = (190, 90, 590, 300)
        d2 = (120, 90, 520, 300)
        s1 = (190, 300, 590, 90)
        e1 = (390, 195)
        e2 = (355, 214)
        arrow = (300, 135, 220, 135)
        result = "Lower price and lower quantity"
        labels = {"d1": (600, 304), "d2": (530, 304), "s1": (598, 88)}
    elif demand_increase:
        d1 = (120, 90, 520, 300)
        d2 = (190, 90, 590, 300)
        s1 = (190, 300, 590, 90)
        e1 = (355, 214)
        e2 = (390, 195)
        arrow = (220, 135, 300, 135)
        result = "Higher price and higher quantity"
        labels = {"d1": (530, 304), "d2": (600, 304), "s1": (598, 88)}
    elif supply_decrease:
        d1 = (190, 90, 590, 300)
        s1 = (160, 300, 560, 90)
        s2 = (230, 300, 630, 90)
        e1 = (370, 185)
        e2 = (405, 166)
        arrow = (320, 145, 395, 105)
        result = "Higher price and lower quantity"
        labels = {"d1": (600, 304), "s1": (566, 88), "s2": (636, 88)}
    elif supply_increase:
        d1 = (190, 90, 590, 300)
        s1 = (230, 300, 630, 90)
        s2 = (160, 300, 560, 90)
        e1 = (405, 166)
        e2 = (370, 185)
        arrow = (395, 105, 320, 145)
        result = "Lower price and higher quantity"
        labels = {"d1": (600, 304), "s1": (636, 88), "s2": (566, 88)}
    else:
        return ""

    price_lines = [(e1, "P1"), (e2, "P2")]
    quantity_lines = [(e1, "Q1"), (e2, "Q2")]

    if shift_curve == "demand":
        shifted_curve = f'<line x1="{d2[0]}" y1="{d2[1]}" x2="{d2[2]}" y2="{d2[3]}" stroke="#2563eb" stroke-width="4"/>'
        original_curve = f'<line x1="{d1[0]}" y1="{d1[1]}" x2="{d1[2]}" y2="{d1[3]}" stroke="#1f2937" stroke-width="4"/>'
        supply_curves = f'<line x1="{s1[0]}" y1="{s1[1]}" x2="{s1[2]}" y2="{s1[3]}" stroke="#1f2937" stroke-width="4"/>'
        labels_svg = f'''
        <text x="{labels["d1"][0]}" y="{labels["d1"][1]}" font-size="22" font-weight="700" fill="#1f2937">D1</text>
        <text x="{labels["d2"][0]}" y="{labels["d2"][1]}" font-size="22" font-weight="700" fill="#2563eb">D2</text>
        <text x="{labels["s1"][0]}" y="{labels["s1"][1]}" font-size="22" font-weight="700" fill="#1f2937">S1</text>'''
        curves_svg = original_curve + shifted_curve + supply_curves
    else:
        original_curve = f'<line x1="{s1[0]}" y1="{s1[1]}" x2="{s1[2]}" y2="{s1[3]}" stroke="#1f2937" stroke-width="4"/>'
        shifted_curve = f'<line x1="{s2[0]}" y1="{s2[1]}" x2="{s2[2]}" y2="{s2[3]}" stroke="#2563eb" stroke-width="4"/>'
        demand_curve = f'<line x1="{d1[0]}" y1="{d1[1]}" x2="{d1[2]}" y2="{d1[3]}" stroke="#1f2937" stroke-width="4"/>'
        labels_svg = f'''
        <text x="{labels["d1"][0]}" y="{labels["d1"][1]}" font-size="22" font-weight="700" fill="#1f2937">D1</text>
        <text x="{labels["s1"][0]}" y="{labels["s1"][1]}" font-size="22" font-weight="700" fill="#1f2937">S1</text>
        <text x="{labels["s2"][0]}" y="{labels["s2"][1]}" font-size="22" font-weight="700" fill="#2563eb">S2</text>'''
        curves_svg = demand_curve + original_curve + shifted_curve

    guides = []
    for (x, y), label in price_lines:
        guides.append(f'<line x1="90" y1="{y}" x2="{x}" y2="{y}" stroke="#64748b" stroke-width="2" stroke-dasharray="6 6"/>')
        guides.append(f'<text x="52" y="{y + 6}" font-size="18" font-weight="700" fill="#334155">{label}</text>')
    for (x, y), label in quantity_lines:
        guides.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="330" stroke="#64748b" stroke-width="2" stroke-dasharray="6 6"/>')
        guides.append(f'<text x="{x - 12}" y="365" font-size="18" font-weight="700" fill="#334155">{label}</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420" role="img">
    <defs>
        <marker id="axisArrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#111827"/>
        </marker>
        <marker id="shiftArrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#dc2626"/>
        </marker>
    </defs>
    <rect x="0" y="0" width="720" height="420" fill="#ffffff"/>
    <text x="360" y="30" text-anchor="middle" font-size="20" font-weight="800" fill="#111827">Demand and Supply Diagram</text>
    <line x1="90" y1="330" x2="650" y2="330" stroke="#111827" stroke-width="3" marker-end="url(#axisArrow)"/>
    <line x1="90" y1="330" x2="90" y2="55" stroke="#111827" stroke-width="3" marker-end="url(#axisArrow)"/>
    <text x="650" y="375" text-anchor="end" font-size="20" font-weight="800" fill="#111827">Quantity</text>
    <text x="38" y="62" font-size="20" font-weight="800" fill="#111827">Price</text>
    {curves_svg}
    {"".join(guides)}
    <circle cx="{e1[0]}" cy="{e1[1]}" r="6" fill="#111827"/>
    <circle cx="{e2[0]}" cy="{e2[1]}" r="6" fill="#2563eb"/>
    <text x="{e1[0] + 10}" y="{e1[1] - 10}" font-size="18" font-weight="800" fill="#111827">E1</text>
    <text x="{e2[0] + 10}" y="{e2[1] + 24}" font-size="18" font-weight="800" fill="#2563eb">E2</text>
    {labels_svg}
    <line x1="{arrow[0]}" y1="{arrow[1]}" x2="{arrow[2]}" y2="{arrow[3]}" stroke="#dc2626" stroke-width="4" marker-end="url(#shiftArrow)"/>
    <text x="360" y="404" text-anchor="middle" font-size="18" font-weight="800" fill="#065f46">{result}</text>
</svg>'''


def _apply_deterministic_diagrams(data: dict, section: str, source_context: str) -> dict:
    parts = data.get("detected_parts")
    if not isinstance(parts, list):
        return data

    for part in parts:
        if not isinstance(part, dict):
            continue
        part.setdefault("diagram_svg", None)
        part_text = " ".join(str(part.get(key, "")) for key in ("part", "question", "answer"))
        
        # Determine if this part actually asks for a diagram
        if len(parts) == 1:
            asks = _asks_for_diagram(part_text) or _asks_for_diagram(source_context)
        else:
            asks = _asks_for_diagram(part_text)
            
        if not asks:
            part["diagram_svg"] = None
            continue
            
        if section == "A":
            shift = _infer_market_shift(part_text)
            if not shift:
                shift = _infer_market_shift(source_context)
            if shift:
                part["diagram_svg"] = _market_diagram_svg(*shift)
            else:
                part["diagram_svg"] = None

    return data


def _extract_image_context(image_base64: str, section: str, index: int, total: int) -> str:
    system = f"""{PAPER2_SYSTEM_PROMPT}

This step is extraction only. Read image {index} of {total} for Section {section}.
Transcribe ALL visible case material, diagrams/tables, question parts, command words, and marks completely. Do not skip or summarize any parts.
If a question part asks the student to draw/sketch/label/show/illustrate a diagram, copy that requirement exactly.
If marks are visible, copy them exactly. If marks are not visible, say 'marks not visible'.
Do not answer yet."""
    user_msg = "Extract the entire Paper 2 question context from this image. Transcribe all visible parts."

    return llm.generate_vision_response(system, user_msg, image_base64)


def answer_paper2_text(section: str, query: str) -> dict:
    section = section.upper()
    inferred_parts = _infer_section_b_marks(query) if section == "B" else []
    context = _get_context(query)
    system = f"{PAPER2_SYSTEM_PROMPT}\n\n### SYLLABUS CONTEXT:\n{context}"
    user_msg = f"""Answer this Economics Paper 2 Section {section} typed question.

Typed question:
{query}

Marks rule:
- For Section B typed questions, infer marks from command words:
  Define = 2, Explain = 4, Analyze/Analyse = 6, Discuss = 8.
- Inferred parts: {json.dumps(inferred_parts, ensure_ascii=False)}
- If no command word is clear, answer cautiously and set marks to null.
"""
    raw = llm.generate_response(system, user_msg, max_tokens=2500)
    result = _extract_json(raw, section, "text", "command word inference")
    return _apply_deterministic_diagrams(result, section, query)


def answer_paper2_images(section: str, image_base64_list: list[str], query: str = "") -> dict:
    section = section.upper()
    total = len(image_base64_list)
    extracted_contexts = []

    for index, image_base64 in enumerate(image_base64_list, start=1):
        extracted = _extract_image_context(image_base64, section, index, total)
        extracted_contexts.append(f"### IMAGE {index} OF {total}\n{extracted}")

    combined_context = "\n\n".join(extracted_contexts)
    syllabus_context = _get_context(f"{query}\n{combined_context}")
    system = f"{PAPER2_SYSTEM_PROMPT}\n\n### SYLLABUS CONTEXT:\n{syllabus_context}"

    section_rule = (
        "Section A may have up to 3 images from the same data-response question. Maintain context across all images."
        if section == "A"
        else "Section B image mode uses one uploaded image. Use the marks visible in the image."
    )

    user_msg = f"""You MUST identify and answer ALL question parts present in the image context of this Economics Paper 2 Section {section} exam. Do not skip any parts (e.g. answer all of part a, b, c, d, e, f if they are visible in the context).

{section_rule}
Use visible marks beside each part. Keep every answer aligned with the O-Level mark demand.
For Section A only: if any part asks to draw/sketch/label/show/illustrate a diagram, provide the written answer and a clean labelled SVG in that part's diagram_svg field.
If a part does not ask for a diagram, set diagram_svg to null.
For a decrease in demand, draw D1 shifting left to D2, supply unchanged, E2 below-left of E1, P2 below P1, and Q2 left of Q1.
For an increase in demand, draw D1 shifting right to D2, supply unchanged, E2 above-right of E1, P2 above P1, and Q2 right of Q1.
For a decrease in supply, draw S1 shifting left/up to S2, demand unchanged, E2 above-left of E1, P2 above P1, and Q2 left of Q1.
For an increase in supply, draw S1 shifting right/down to S2, demand unchanged, E2 below-right of E1, P2 below P1, and Q2 right of Q1.

Combined extracted image context:
{combined_context}

User note/instructions (use this to guide your answers, but you MUST still output answers for all visible question parts):
{query or "No extra note provided."}
"""
    raw = llm.generate_response(system, user_msg, max_tokens=3000)
    result = _extract_json(raw, section, "image", "image marks")
    return _apply_deterministic_diagrams(result, section, f"{query}\n{combined_context}")
