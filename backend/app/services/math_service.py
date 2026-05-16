"""
Math Solver Service
Parses student questions and returns structured step-by-step solutions via the LLM.
"""

import json
import re
from app.services.llm_service import LLMService

llm = LLMService()

# ── Concept keys the LLM is allowed to reference ──────────────────────────────
VALID_CONCEPT_KEYS = {
    "addition", "subtraction", "multiplication", "division", "bodmas",
    "fractions", "percentages", "ratio", "proportion", "hcf", "lcm",
    "prime_factorisation", "standard_form", "rounding", "square_root", "indices",
    "expanding_brackets", "factorisation", "quadratic_formula", "completing_the_square",
    "linear_equations", "simultaneous_equations", "inequalities", "algebraic_fractions",
    "sequences", "functions", "area", "perimeter", "volume", "pythagoras",
    "angles", "parallel_lines", "circle_theorems", "similarity", "congruence",
    "transformations", "vectors", "trigonometry", "sine_rule", "cosine_rule",
    "bearing", "gradient", "y_intercept", "straight_line_graph", "quadratic_graph",
    "distance_time_graph", "mean", "median", "mode", "range", "probability",
    "histogram", "cumulative_frequency", "scatter_graph", "differentiation",
    "integration", "matrix", "loci", "set_notation",
}

SYSTEM_PROMPT = """You are an expert Cambridge O-Level / IGCSE Mathematics tutor (syllabus 4024 / 0580).
Your job is to solve exam questions step-by-step in the style of a mark scheme examiner answer,
calibrating depth to the number of marks awarded.

STRICT OUTPUT RULES — follow exactly:
1. Return ONLY valid JSON. No preamble, no explanation outside the JSON.
2. The JSON must have exactly this shape:
{
  "steps": [
    {
      "step_number": 1,
      "description": "Short phrase of what we are doing (e.g. 'Write the quadratic formula')",
      "expression": "The math expression or calculation for this step, use plain text math notation",
      "concept_key": "one_of_the_valid_keys_below_or_null"
    }
  ],
  "final_answer": "The final numerical or algebraic answer with units if applicable",
  "mark_commentary": "Brief note on how marks are typically awarded for this question"
}
3. Depth guideline:
   - 1 mark  → 1–2 steps
   - 2 marks → 2–4 steps
   - 3 marks → 3–5 steps
   - 4 marks → 4–7 steps
   - 5–6 marks → 6–10 steps
   - 7+ marks → 8–14 steps
4. concept_key must be one of the following keys ONLY (or null if no relevant concept):
   addition, subtraction, multiplication, division, bodmas, fractions, percentages,
   ratio, proportion, hcf, lcm, prime_factorisation, standard_form, rounding,
   square_root, indices, expanding_brackets, factorisation, quadratic_formula,
   completing_the_square, linear_equations, simultaneous_equations, inequalities,
   algebraic_fractions, sequences, functions, area, perimeter, volume, pythagoras,
   angles, parallel_lines, circle_theorems, similarity, congruence, transformations,
   vectors, trigonometry, sine_rule, cosine_rule, bearing, gradient, y_intercept,
   straight_line_graph, quadratic_graph, distance_time_graph, mean, median, mode,
   range, probability, histogram, cumulative_frequency, scatter_graph,
   differentiation, integration, matrix, loci, set_notation
5. Use plain Unicode maths notation in expressions (e.g. x² not x^2, √ not sqrt, π not pi).
   Write fractions as a/b. Write superscripts using Unicode superscript digits where possible.
6. Be precise — give exact answers where possible (e.g. 2√3, not 3.46).
7. GRAPH DRAWING: If the question asks to 'draw', 'plot', or 'sketch' a graph, you MUST include the specific instruction: "Please go to the Image section of math for graph drawing tools." in your `final_answer`. You should still provide necessary calculations or coordinates in the steps.
8. UNITS: You MUST include relevant units (e.g. cm, m², kg, s, °) in the `final_answer` if they are provided in the question or are standard for the result.
"""


def _extract_json(raw: str) -> str:
    """Extract the first {...} JSON block from the LLM response."""
    # Try to find JSON object boundaries
    start = raw.find("{")
    if start == -1:
        return raw
    # Find matching closing brace
    depth = 0
    for i, ch in enumerate(raw[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return raw[start : i + 1]
    return raw[start:]


def _validate_steps(steps: list) -> list:
    """Sanitize step list — ensure concept_key is valid."""
    cleaned = []
    for step in steps:
        ck = step.get("concept_key")
        if ck and ck.lower() not in VALID_CONCEPT_KEYS:
            ck = None
        cleaned.append({
            "step_number": int(step.get("step_number", len(cleaned) + 1)),
            "description": str(step.get("description", "")),
            "expression": str(step.get("expression", "")),
            "concept_key": ck.lower() if ck else None,
        })
    return cleaned


def solve_math_question(question: str, question_number: int, marks: int) -> dict:
    """
    Main entry point: send question to LLM and return structured solution.
    """
    # Pre-check for graph drawing requests
    graph_keywords = ["draw", "plot", "sketch"]
    q_lower = question.lower()
    if any(kw in q_lower for kw in graph_keywords):
        return {
            "question_number": question_number,
            "marks": marks,
            "steps": [
                {
                    "step_number": 1,
                    "description": "Graph Drawing Instruction",
                    "expression": "Please go to the Image section of math for graph drawing tools.",
                    "concept_key": None,
                }
            ],
            "final_answer": "Please go to the Image section of math for graph drawing tools.",
            "mark_commentary": "Interactive graph drawing is handled in the specialized Vision/Image section.",
            "raw_question": question,
        }

    user_prompt = (
        f"Question {question_number} [{marks} mark{'s' if marks != 1 else ''}]\n\n"
        f"{question.strip()}\n\n"
        f"Provide a complete, mark-scheme-quality step-by-step solution calibrated for {marks} mark(s)."
    )

    raw = llm.generate_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=3000,
        temperature=0.2,
    )

    # Parse JSON
    try:
        json_str = _extract_json(raw)
        data = json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        # Fallback: return raw text as a single step
        return {
            "question_number": question_number,
            "marks": marks,
            "steps": [
                {
                    "step_number": 1,
                    "description": "AI response",
                    "expression": raw[:1000],
                    "concept_key": None,
                }
            ],
            "final_answer": "See step above",
            "mark_commentary": f"For {marks} mark(s)",
            "raw_question": question,
        }

    steps = _validate_steps(data.get("steps", []))
    return {
        "question_number": question_number,
        "marks": marks,
        "steps": steps,
        "final_answer": str(data.get("final_answer", "")),
        "mark_commentary": str(data.get("mark_commentary", f"[{marks} mark(s)]")),
        "raw_question": question,
    }
