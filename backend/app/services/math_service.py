"""
Math Solver Service
Parses student questions and returns structured step-by-step solutions via the LLM.
"""

import json
import re
import os
import base64
import io
import math
from PIL import Image
try:
    import pytesseract
except ImportError:
    pytesseract = None

from app.services.llm_service import LLMService
from app.utils.nlp_utils import nlp_processor
from app.repositories.data_repository import DataRepository

llm = LLMService()
data_repo = DataRepository()

# Load Math Dataset
MATH_DATASET = data_repo.get_math_data()

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
      "part": "a",
      "description": "Short phrase (e.g. '(a) [2 marks] Write the quadratic formula')",
      "expression": "x = (-b ± √(b² - 4ac)) / 2a",
      "concept_key": "quadratic_formula"
    }
  ],
  "final_answer": "The final numerical or algebraic answer with units if applicable",
  "mark_commentary": "Brief note on how marks are typically awarded for this question",
  "detected_marks": 0,
  "visual_data": "STRICTLY ONLY SVG markup or null. If asked to draw/sketch, generate clean <svg> markup here."
}
3. Depth guideline:
   - 1 mark  → 1–2 steps
   - 2 marks → 2–4 steps
   - 3 marks → 3–5 steps
   - 4-5 marks → 5–8 steps
   - 6+ marks → 8–12 steps
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
7. MANDATORY EXPRESSIONS: Every step MUST have a non-empty `expression` field. If the step is descriptive, use relevant coordinates, e.g., (x,y) = (1,2).
8. MULTI-PART QUESTIONS: If the image contains a question with subparts ((a), (b), (i), (ii), etc.), identify each part and its visible marks. For each part:
   - mention the part label and allocated marks in the description,
   - answer the part separately,
   - if marks are visible, provide exactly that many distinct mark-worthy points for that part.
9. DETECTED_MARKS: If multiple part marks are visible, set `detected_marks` to the total of all visible part marks. If no marks are visible, use the provided `marks` as an overall depth guide.
10. GRAPH DRAWING / DIAGRAMS: If the question asks to 'draw', 'plot', 'sketch', 'construct', 'show a diagram', or perform transformations ('reflect', 'rotate', 'translate', 'enlarge'), you MUST generate a high-quality SVG in the `visual_data` field. The SVG should:
   - Use a transparent background (<svg background="none" ...>).
   - Use light/white stroke/fill (e.g. #fbbf24 or white) for visibility against dark backgrounds.
   - Include axes, scale markers, and labels.
   - Be responsive (use viewBox, width="100%", height="auto").
11. UNITS: You MUST include relevant units (e.g. cm, m², kg, s, °) in the `final_answer` if they are provided in the question or are standard for the result.
12. IMAGE THEME: Always prioritize the question and marks written INSIDE the image.
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


def _normalize_extracted_math_text(text: str) -> str:
    """Normalize OCR/vision text by restoring common missing spaces and common math phrases."""
    if not text:
        return ""

    text = text.replace("\n", " ")
    text = re.sub(r"([A-Za-z])(?=\d)", r"\1 ", text)
    text = re.sub(r"(\d)(?=[A-Za-z])", r"\1 ", text)
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    text = re.sub(r"\s+", " ", text).strip()

    replacements = {
        r"drawaline": "draw a line",
        r"lineofbestfit": "line of best fit",
        r"bestfit": "best fit",
        r"plottedpoints": "plotted points",
        r"scatterdiagram": "scatter diagram",
        r"scattergraph": "scatter graph",
        r"tothex": "to the x",
        r"tointersectthe": "to intersect the",
        r"straightlinethat": "straight line that",
        r"remaining3": "remaining 3",
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def _extract_coordinate_pairs(text: str) -> list[tuple[float, float]]:
    """Extract coordinate pairs like (x, y) from OCR/vision text."""
    points = []
    if not text:
        return points

    for match in re.finditer(r"\(?\s*([+-]?\d+(?:\.\d+)?)\s*,\s*([+-]?\d+(?:\.\d+)?)\s*\)?", text):
        try:
            x = float(match.group(1))
            y = float(match.group(2))
            points.append((x, y))
        except ValueError:
            continue

    return points


def extract_text_from_vision(image_base64: str) -> str:
    """Extract visible text from the image using the configured vision model."""
    system_prompt = """You are a math image text extractor.
    Transcribe all visible text, numbers, symbols, coordinates and equation labels exactly as they appear.
    Return plain text only, with no explanation.
    """
    user_prompt = "Transcribe the text from this image."
    try:
        raw = llm.generate_vision_response(system_prompt, user_prompt, image_base64)
        return raw.strip()
    except Exception as e:
        print(f"Vision OCR Error: {e}")
        return ""


def _extract_quadratic_equation(text: str) -> tuple[float, float, float] | None:
    """Parse a quadratic equation from standard or vertex form."""
    if not text:
        return None

    clean = text.replace(" ", "")
    clean = clean.replace("x²", "x^2").replace("X²", "x^2").replace("X^2", "x^2")
    clean = clean.lower()
    clean = clean.replace("f(x)=", "y=").replace("=f(x)", "=y")

    if "=y" in clean and not clean.startswith("y="):
        left, right = clean.split("=y", 1)
        clean = f"y={left}"

    def parse_coef(value: str, default: float = 1.0) -> float:
        if value in ("", "+"):
            return default
        if value == "-":
            return -default
        try:
            return float(value)
        except ValueError:
            return default

    # vertex form: y=a(x-h)^2+k or y=a(x+h)^2+k
    vertex_match = re.search(r"y=([+-]?\d*\.?\d*)\(x([+-]\d*\.?\d*)\)\^2([+-]?\d*\.?\d*)", clean)
    if vertex_match:
        a = parse_coef(vertex_match.group(1))
        raw_h = float(vertex_match.group(2))
        h = -raw_h
        k = parse_coef(vertex_match.group(3), default=0.0)
        b = -2 * a * h
        c = a * h * h + k
        return a, b, c

    standard_match = re.search(r"y=([+-]?\d*\.?\d*)x\^2([+-]?\d*\.?\d*)x([+-]?\d*\.?\d*)", clean)
    if standard_match:
        a = parse_coef(standard_match.group(1))
        b = parse_coef(standard_match.group(2), default=1.0)
        c = parse_coef(standard_match.group(3), default=0.0)
        return a, b, c

    return None


def _compute_best_fit_line(points: list[tuple[float, float]]) -> tuple[float, float] | None:
    """Return slope and intercept for the least-squares best fit line."""
    if len(points) < 2:
        return None

    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    n = len(points)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in points)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    if denominator == 0:
        return None

    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    return slope, intercept


def _render_quadratic_svg(a: float, b: float, c: float, title: str = None) -> str:
    """Render a neat SVG for a quadratic function and label the vertex and y-intercept."""
    width = 760
    height = 460
    padding = 64

    x_vertex = -b / (2 * a)
    y_vertex = a * x_vertex**2 + b * x_vertex + c

    x_min = min(-5, x_vertex - 4)
    x_max = max(5, x_vertex + 4)
    discriminant = b**2 - 4 * a * c
    if discriminant >= 0:
        root1 = (-b - discriminant**0.5) / (2 * a)
        root2 = (-b + discriminant**0.5) / (2 * a)
        x_min = min(x_min, root1, root2)
        x_max = max(x_max, root1, root2)

    x_min = min(x_min, 0)
    x_max = max(x_max, 0)
    x_padding = max(1.0, (x_max - x_min) * 0.08)
    x_min -= x_padding
    x_max += x_padding
    x_span = x_max - x_min if x_max != x_min else 1

    y_all = [a * x**2 + b * x + c for x in [x_min, x_max, 0, x_vertex]]
    y_all.append(0)
    y_min = min(y_all)
    y_max = max(y_all)
    y_padding = max(1.0, (y_max - y_min) * 0.12)
    y_min -= y_padding
    y_max += y_padding
    y_span = y_max - y_min if y_max != y_min else 1

    def px_x(x):
        return padding + (x - x_min) / x_span * (width - 2 * padding)

    def px_y(y):
        return height - padding - (y - y_min) / y_span * (height - 2 * padding)

    x_axis_y = px_y(0)
    y_axis_x = px_x(0)

    points = []
    step = max((x_max - x_min) / 80, 0.1)
    x = x_min
    while x <= x_max + 1e-9:
        y = a * x**2 + b * x + c
        points.append((x, y))
        x += step

    path_data = " ".join(f"{px_x(x):.2f},{px_y(y):.2f}" for x, y in points)
    axis_color = "#f8fafc"
    grid_color = "rgba(248,250,252,0.12)"
    curve_color = "#f59e0b"
    marker_color = "#38bdf8"

    y_intercept = (0, c)
    vertex = (x_vertex, y_vertex)

    labels = [
        f"<text x=\"{px_x(y_intercept[0]) + 12:.2f}\" y=\"{px_y(y_intercept[1]) - 8:.2f}\" fill=\"{marker_color}\" font-size=\"12\" text-anchor=\"start\">(0,{y_intercept[1]:.0f})</text>",
        f"<text x=\"{px_x(vertex[0]) + 12:.2f}\" y=\"{px_y(vertex[1]) - 8:.2f}\" fill=\"{marker_color}\" font-size=\"12\" text-anchor=\"start\">({vertex[0]:.2f},{vertex[1]:.0f})</text>",
    ]

    ticks = []
    for x_tick in range(int(math.floor(x_min)), int(math.ceil(x_max)) + 1):
        ticks.append(f"<line x1=\"{px_x(x_tick):.2f}\" y1=\"{x_axis_y - 4:.2f}\" x2=\"{px_x(x_tick):.2f}\" y2=\"{x_axis_y + 4:.2f}\" stroke=\"{axis_color}\" stroke-width=1 />")
        ticks.append(f"<text x=\"{px_x(x_tick):.2f}\" y=\"{x_axis_y + 18:.2f}\" fill=\"{axis_color}\" font-size=\"12\" text-anchor=\"middle\">{x_tick}</text>")
    for y_tick in range(int(math.floor(y_min)), int(math.ceil(y_max)) + 1):
        ticks.append(f"<line x1=\"{y_axis_x - 4:.2f}\" y1=\"{px_y(y_tick):.2f}\" x2=\"{y_axis_x + 4:.2f}\" y2=\"{px_y(y_tick):.2f}\" stroke=\"{axis_color}\" stroke-width=1 />")
        ticks.append(f"<text x=\"{y_axis_x - 10:.2f}\" y=\"{px_y(y_tick) + 4:.2f}\" fill=\"{axis_color}\" font-size=\"12\" text-anchor=\"end\">{y_tick}</text>")

    title_markup = f"<text x=\"50%\" y=\"24\" fill=\"{axis_color}\" font-size=\"16\" text-anchor=\"middle\" font-weight=\"700\">{title}</text>" if title else ""

    svg = f"""<svg viewBox=\"0 0 {width} {height}\" width=\"100%\" height=\"auto\" background=\"none\" xmlns=\"http://www.w3.org/2000/svg\">
      <rect x=\"0\" y=\"0\" width=\"100%\" height=\"100%\" fill=\"transparent\" />
      {title_markup}
      <line x1=\"{y_axis_x:.2f}\" y1=\"{padding}\" x2=\"{y_axis_x:.2f}\" y2=\"{height - padding}\" stroke=\"{axis_color}\" stroke-width=\"2\" />
      <line x1=\"{padding}\" y1=\"{x_axis_y:.2f}\" x2=\"{width - padding}\" y2=\"{x_axis_y:.2f}\" stroke=\"{axis_color}\" stroke-width=\"2\" />
      {''.join(ticks)}
      <polyline points=\"{path_data}\" fill=\"none\" stroke=\"{curve_color}\" stroke-width=\"2.5\" stroke-linejoin=\"round\" stroke-linecap=\"round\" />
      <circle cx=\"{px_x(y_intercept[0]):.2f}\" cy=\"{px_y(y_intercept[1]):.2f}\" r=\"4\" fill=\"{marker_color}\" stroke=\"#ffffff\" stroke-width=\"1.2\" />
      <circle cx=\"{px_x(vertex[0]):.2f}\" cy=\"{px_y(vertex[1]):.2f}\" r=\"4\" fill=\"{marker_color}\" stroke=\"#ffffff\" stroke-width=\"1.2\" />
      {''.join(labels)}
    </svg>"""
    return svg


def _render_svg_plot(points: list[tuple[float, float]], title: str = None, line: tuple[float, float] | None = None) -> str:
    """Generate a clean SVG plot for extracted graph points."""
    if not points:
        return ""

    width = 760
    height = 460
    padding = 52
    min_x = min(x for x, _ in points)
    max_x = max(x for x, _ in points)
    min_y = min(y for _, y in points)
    max_y = max(y for _, y in points)
    min_x = min(min_x, 0)
    max_x = max(max_x, 0)
    min_y = min(min_y, 0)
    max_y = max(max_y, 0)

    x_padding = max(1.0, (max_x - min_x) * 0.08)
    y_padding = max(1.0, (max_y - min_y) * 0.08)
    min_x -= x_padding
    max_x += x_padding
    min_y -= y_padding
    max_y += y_padding

    x_span = max_x - min_x if max_x != min_x else 1
    y_span = max_y - min_y if max_y != min_y else 1

    def px_x(x):
        return padding + (x - min_x) / x_span * (width - 2 * padding)

    def px_y(y):
        return height - padding - (y - min_y) / y_span * (height - 2 * padding)

    x_axis_y = px_y(0)
    y_axis_x = px_x(0)

    polyline = " ".join(f"{px_x(x):.2f},{px_y(y):.2f}" for x, y in points)
    axis_color = "#f8fafc"
    grid_color = "rgba(248,250,252,0.12)"
    point_color = "#f59e0b"

    line_markup = ""
    if line is not None:
        slope, intercept = line
        x1 = min_x
        y1 = slope * x1 + intercept
        x2 = max_x
        y2 = slope * x2 + intercept
        line_markup = f"<line x1=\"{px_x(x1):.2f}\" y1=\"{px_y(y1):.2f}\" x2=\"{px_x(x2):.2f}\" y2=\"{px_y(y2):.2f}\" stroke=\"#38bdf8\" stroke-width=2 stroke-dasharray=\"6 4\" />"

    labels = []
    labels.append(f"<text x=\"{y_axis_x - 10:.2f}\" y=\"{px_y(min_y) + 4:.2f}\" fill=\"{axis_color}\" font-size=\"12\" text-anchor=\"middle\">{min_y}</text>")
    labels.append(f"<text x=\"{y_axis_x - 10:.2f}\" y=\"{px_y(max_y) + 4:.2f}\" fill=\"{axis_color}\" font-size=\"12\" text-anchor=\"middle\">{max_y}</text>")
    labels.append(f"<text x=\"{px_x(min_x):.2f}\" y=\"{x_axis_y + 18:.2f}\" fill=\"{axis_color}\" font-size=\"12\" text-anchor=\"middle\">{min_x}</text>")
    labels.append(f"<text x=\"{px_x(max_x):.2f}\" y=\"{x_axis_y + 18:.2f}\" fill=\"{axis_color}\" font-size=\"12\" text-anchor=\"middle\">{max_x}</text>")

    points_markup = "".join(
        f"<circle cx=\"{px_x(x):.2f}\" cy=\"{px_y(y):.2f}\" r=\"4\" fill=\"{point_color}\" stroke=\"#ffffff\" stroke-width=\"1.4\" />"
        for x, y in points
    )

    title_markup = f"<text x=\"50%\" y=\"24\" fill=\"{axis_color}\" font-size=\"16\" text-anchor=\"middle\" font-weight=\"700\">{title}</text>" if title else ""

    svg = f"""<svg viewBox=\"0 0 {width} {height}\" width=\"100%\" height=\"auto\" background=\"none\" xmlns=\"http://www.w3.org/2000/svg\">
      <rect x=\"0\" y=\"0\" width=\"100%\" height=\"100%\" fill=\"transparent\" />
      {title_markup}
      <line x1=\"{y_axis_x:.2f}\" y1=\"{padding:.2f}\" x2=\"{y_axis_x:.2f}\" y2=\"{height - padding:.2f}\" stroke=\"{axis_color}\" stroke-width=2 />
      <line x1=\"{padding:.2f}\" y1=\"{x_axis_y:.2f}\" x2=\"{width - padding:.2f}\" y2=\"{x_axis_y:.2f}\" stroke=\"{axis_color}\" stroke-width=2 />
      <line x1=\"{padding}\" y1=\"{padding + 40}\" x2=\"{width - padding}\" y2=\"{padding + 40}\" stroke=\"{grid_color}\" stroke-width=1 />
      <line x1=\"{padding}\" y1=\"{height - padding - 40}\" x2=\"{width - padding}\" y2=\"{height - padding - 40}\" stroke=\"{grid_color}\" stroke-width=1 />
      <line x1=\"{padding + 40}\" y1=\"{padding}\" x2=\"{padding + 40}\" y2=\"{height - padding}\" stroke=\"{grid_color}\" stroke-width=1 />
      <line x1=\"{width - padding - 40}\" y1=\"{padding}\" x2=\"{width - padding - 40}\" y2=\"{height - padding}\" stroke=\"{grid_color}\" stroke-width=1 />
      {line_markup}
      <polyline points=\"{polyline}\" fill=\"none\" stroke=\"{point_color}\" stroke-width=2.5 stroke-linejoin=round stroke-linecap=round />
      {points_markup}
      {''.join(labels)}
    </svg>"""
    return svg


def _build_graph_visual(query: str, extracted_text: str) -> str | None:
    graph_keywords = ["draw", "plot", "sketch", "diagram", "curve", "graph", "best fit", "scatter"]
    content = f"{query} {extracted_text}".lower()
    if not any(kw in content for kw in graph_keywords):
        return None

    combined_text = f"{query} {extracted_text}"
    quadratic = _extract_quadratic_equation(combined_text)
    if quadratic:
        a, b, c = quadratic
        return _render_quadratic_svg(a, b, c, title="Quadratic graph")

    points = _extract_coordinate_pairs(combined_text)
    if len(points) >= 2:
        line = _compute_best_fit_line(points)
        return _render_svg_plot(points, title="Extracted graph from image", line=line)

    return None


def get_math_context(query: str, extracted_text: str = "") -> str:
    """Find relevant O-Level syllabus tips and patterns based on the query."""
    context = ""
    processed_query = nlp_processor.preprocess(f"{query} {extracted_text}")
    query_set = set(processed_query)
    
    topics = MATH_DATASET.get("topics", {})
    matched_tips = []
    
    for topic_name, topic_data in topics.items():
        topic_keywords = set(topic_data.get("keywords", []))
        if query_set.intersection(topic_keywords):
            matched_tips.append(f"[{topic_name.upper()}] {topic_data.get('examiner_tips')}")
    
    if matched_tips:
        context += "\n### Relevant O-Level Examiner Tips:\n"
        for tip in matched_tips[:3]:
            context += f"- {tip}\n"
            
    # Check for marking patterns
    marking_patterns = MATH_DATASET.get("marking_patterns", {})
    for action, detail in marking_patterns.items():
        if action in query.lower() or action in extracted_text.lower():
            context += f"\n- **Marking Rule for '{action}':** {detail}\n"
            
    return context

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
        "visual_data": data.get("visual_data"),
        "raw_question": question,
    }

def extract_text_via_ocr(image_base64: str) -> str:
    """Extract text using a dedicated OCR library (pytesseract)."""
    if pytesseract is None:
        return ""
    
    try:
        image_data = base64.b64decode(image_base64)
        img = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

def check_math_image_relevance(image_base64: str, extracted_text: str = "") -> dict:
    """
    Validate that the image contains math content using OCR, NLP, and Dataset matching.
    """
    if not extracted_text:
        extracted_text = extract_text_via_ocr(image_base64)
    if not extracted_text:
        extracted_text = extract_text_from_vision(image_base64)
    extracted_text = _normalize_extracted_math_text(extracted_text)
    
    # If OCR returns nothing, we use LLM vision for a final relevance check (fallback)
    if not extracted_text:
        system_prompt = """You are a math relevance classifier.
        Check if the image contains:
        1. Mathematical symbols or equations
        2. Graphs (coordinate grids, curves, bar/line charts)
        3. Geometric diagrams (shapes, angles, triangles)
        4. O-Level/IGCSE math past paper layout
        
        Return JSON ONLY: {"relevant": true, "reason": "explain why"} or {"relevant": false, "reason": "explain why"}"""
        user_prompt = "Classify this image for math relevance."
        try:
            raw = llm.generate_vision_response(system_prompt, user_prompt, image_base64)
            # Use regex to find JSON block safely
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return {"relevant": data.get("relevant", False), "reason": f"Vision: {data.get('reason', 'Check successful')}"}
            
            # Text-based fallback if JSON fails
            lowered = raw.lower()
            if any(x in lowered for x in ["relevant: true", "is relevant", "contains math", "has graph"]):
                return {"relevant": True, "reason": "Vision (Text Fallback)"}
                
            return {"relevant": False, "reason": "No math features detected by vision."}
        except Exception as e:
            # If everything else fails, but it's a diagram question, we might want to be lenient
            # but for now, provide a better error
            return {"relevant": False, "reason": f"Vision analysis encountered an error: {str(e)}"}

    # NLP Preprocessing
    keywords = nlp_processor.get_keywords(extracted_text)
    
    # Pattern & Keyword Matching
    matched = False
    relevance_keywords = MATH_DATASET.get("relevance_keywords", [])
    
    # Check for keywords
    for kw in relevance_keywords:
        if kw.lower() in keywords:
            matched = True
            break
            
    # Check for patterns (formulas/symbols)
    if not matched:
        for topic in MATH_DATASET.get("topics", {}).values():
            patterns = topic.get("patterns", [])
            for pattern in patterns:
                if re.search(pattern, extracted_text, re.IGNORECASE):
                    matched = True
                    break
            if matched: break

    return {
        "relevant": matched,
        "reason": "Pattern matched" if matched else "No relevant math symbols, keywords, or patterns found in this image.",
        "extracted_text": extracted_text
    }

def solve_math_image_question(image_base64: str, query: str, marks: int) -> dict:
    """
    Handles math image solving with relevance gate.
    """
    # 1. Relevance Check
    relevance = check_math_image_relevance(image_base64)
    if not relevance.get("relevant"):
        return {
            "error": "Subject Relevance Error",
            "message": f"Uploaded image math se relevant nahi lag rahi. Reason: {relevance.get('reason')}. Please math question, diagram ya formula upload karein.",
            "relevance_reason": relevance.get("reason")
        }

    # 2. Vision Analysis & Solving
    extracted_text = relevance.get("extracted_text", "")
    context = get_math_context(query, extracted_text)
    system_prompt = (
        SYSTEM_PROMPT
        + "\n\nAnalyze the IMAGE and solve the question within it."
        + " Use any extracted text as additional context."
        + " If extracted text spacing is broken, reconstruct the wording while preserving all numeric coordinates exactly."
        + " If the question is multipart, answer each part separately with its part label and marks."
        + " If asked to plot points, draw the exact coordinates and include them in the SVG."
        + " If asked to draw a line of best fit, include that line in visual_data."
        + "\n"
        + context
    )
    user_prompt = (
        f"Extracted text: {extracted_text}\n"
        f"User question: {query}\n"
        f"Solve this image-based math question for {marks} marks."
        " Provide all answers in JSON with the exact question parts and an SVG when drawing is required."
    )
    
    raw = llm.generate_vision_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        image_base64=image_base64
    )

    # 3. Parse and Return
    try:
        json_str = _extract_json(raw)
        data = json.loads(json_str)
        steps = _validate_steps(data.get("steps", []))
        # Use detected marks if available, else fallback
        final_marks = data.get("detected_marks", marks)
        if not final_marks:
            final_marks = marks

        generated_visual = _build_graph_visual(query, extracted_text)
        visual_data = generated_visual if generated_visual else data.get("visual_data")

        return {
            "question_number": 1,
            "marks": final_marks,
            "steps": steps,
            "final_answer": str(data.get("final_answer", "")),
            "mark_commentary": str(data.get("mark_commentary", f"[{final_marks} mark(s)]")),
            "visual_data": visual_data,
            "raw_question": relevance.get("extracted_text", "Image Based Question")
        }
    except Exception as e:
        return {
            "error": "Parsing Error",
            "message": f"Failed to parse AI response: {str(e)}",
            "raw_response": raw
        }
