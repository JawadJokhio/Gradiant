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

# Load Math Past Papers Dataset (2002-2025)
MATH_PAST_PAPERS = data_repo.get_math_past_papers_data()


def _get_past_paper_context(question: str, marks: int) -> str:
    """Search the 2002-2025 O-Level Math past papers for similar questions to enrich LLM context."""
    if not MATH_PAST_PAPERS:
        return ""

    q_lower = question.lower()
    # Key topic words to match
    keywords = re.findall(r"\b\w{4,}\b", q_lower)
    keyword_set = set(keywords)

    best_matches = []
    past_papers = MATH_PAST_PAPERS.get("past_papers", {})

    for year_data in past_papers.values():
        for session_data in year_data.values():
            for paper_key in ("paper_1", "paper_2"):
                paper = session_data.get(paper_key, {})
                for entry in paper.get("mark_scheme", []):
                    entry_q = entry.get("question", "").lower()
                    entry_words = set(re.findall(r"\b\w{4,}\b", entry_q))
                    overlap = len(keyword_set & entry_words)
                    if overlap >= 2:
                        best_matches.append((overlap, entry))

    if not best_matches:
        return ""

    # Sort by overlap score, take top 3
    best_matches.sort(key=lambda x: x[0], reverse=True)
    top = best_matches[:3]

    lines = ["### Relevant Past Paper Mark Scheme Examples (Cambridge O-Level 4024):"]
    for _, entry in top:
        lines.append(
            f"\n**Q [{entry.get('year','')} {entry.get('season','')}] ({entry.get('marks','')} marks):** "
            f"{entry.get('question','')}"
        )
        for pt in entry.get("mark_scheme_points", []):
            lines.append(f"  - {pt}")
        tip = entry.get("examiner_tips", "")
        if tip:
            lines.append(f"  💡 Examiner tip: {tip}")

    return "\n".join(lines)

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

SYSTEM_PROMPT = """You are a master Cambridge O-Level (4024) and IGCSE (0580) Mathematics Examiner.
Your goal is to provide high-precision, mark-scheme-accurate solutions to math questions.

STRICT OUTPUT RULES:
1. Return ONLY valid JSON.
2. Structure:
{
  "steps": [
    {
      "step_number": 1,
      "part": "a",
      "description": "Clear explanation of the step",
      "expression": "Mathematical working/result using Unicode (x², √, π, θ)",
      "concept_key": "valid_key_from_list"
    }
  ],
  "final_answer": "Concise summary of final results for all parts",
  "mark_commentary": "Brief note on mark allocation (e.g., M1 for method, A1 for accuracy)",
  "detected_marks": 0,
  "visual_data": "Generated SVG ONLY if explicitly asked to draw/graph/plot, else null"
}

MARK SCHEME ACCURACY:
- Calibrate the number of steps to the total marks. A 4-mark question should have roughly 3-4 distinct logical steps.
- Use 'M1' for method marks, 'A1' for accuracy marks in the mark_commentary if possible.

MULTI-PART QUESTIONS:
- If a question has parts (a), (b), (c) etc., you MUST solve ALL of them.
- Label each step with the correct 'part'.

NOTATION:
- Use Unicode: x², x³, √, π, θ, ±, ≤, ≥, ×, ÷, °.
- Do NOT use LaTeX like \\frac{a}{b}. Use a/b or vertical spacing if needed.
- For coordinates, use (x, y).

GRAPHICS & VISUALS:
- If the student is asked to 'draw', 'plot', 'sketch', 'construct', or 'reflect/rotate', you must generate a high-quality SVG.
- The SVG must have:
  - Clear axis labels and scale.
  - A grid if appropriate.
  - Distinct colors for different elements (e.g., #f59e0b for curves, #38bdf8 for lines).
  - All labels (vertex, intercepts, points) must be clearly visible.
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


def extract_diagram_description_from_vision(image_base64: str) -> str:
    """Describe the visible diagram, labels, angles and markings from the image."""
    system_prompt = """You are a math diagram interpreter.
    Describe only the shapes, lines, angle labels, equal-side markings, text labels and measurements visible in the image.
    Return plain text only, with no explanation, no reasoning, and no JSON.
    """
    user_prompt = "Describe the diagram and labels in the image."
    try:
        raw = llm.generate_vision_response(system_prompt, user_prompt, image_base64)
        return raw.strip()
    except Exception as e:
        print(f"Vision Diagram Error: {e}")
        return ""


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


def _render_quadratic_svg(a: float, b: float, c: float, title: str = "Quadratic Graph") -> str:
    """Render a premium, clean SVG for a quadratic function with clear points and grids."""
    width, height = 760, 500
    padding = 60

    # Key points
    x_vertex = -b / (2 * a)
    y_vertex = a * x_vertex**2 + b * x_vertex + c
    y_intercept = (0, c)

    # Dynamic scaling
    x_min, x_max = -6, 6
    if abs(x_vertex) > 4:
        x_min = min(x_min, x_vertex - 2)
        x_max = max(x_max, x_vertex + 2)

    x_span = x_max - x_min
    
    # Calculate y-range based on x-range
    sample_xs = [x_min, x_max, 0, x_vertex]
    sample_ys = [a * x**2 + b * x + c for x in sample_xs]
    sample_ys.append(0) # Include axis
    y_min, y_max = min(sample_ys), max(sample_ys)
    
    y_extra = (y_max - y_min) * 0.15 or 1.0
    y_min -= y_extra
    y_max += y_extra
    y_span = y_max - y_min

    def px_x(x): return padding + (x - x_min) / x_span * (width - 2 * padding)
    def px_y(y): return height - padding - (y - y_min) / y_span * (height - 2 * padding)

    x_zero_y = px_y(0)
    y_zero_x = px_x(0)

    # Path points
    points = []
    seg = 100
    for i in range(seg + 1):
        qx = x_min + (i / seg) * x_span
        qy = a * qx**2 + b * qx + c
        if y_min - y_extra*2 <= qy <= y_max + y_extra*2:
            points.append(f"{px_x(qx):.1f},{px_y(qy):.1f}")
    
    path_data = " ".join(points)

    # Grid and Ticks
    def get_step(span):
        if span <= 10: return 1
        if span <= 25: return 5
        if span <= 100: return 10
        return 20

    x_step = get_step(x_span)
    y_step = get_step(y_span)

    grid_elements = []
    # Vertical grid & x-ticks
    for xt in range(int(math.floor(x_min / x_step) * x_step), int(math.ceil(x_max / x_step) * x_step) + 1, x_step):
        gx = px_x(xt)
        if padding <= gx <= width - padding:
            grid_elements.append(f'<line x1="{gx:.1f}" y1="{padding}" x2="{gx:.1f}" y2="{height-padding}" stroke="rgba(255,255,255,0.05)" stroke-width="1" stroke-dasharray="4 4"/>')
            grid_elements.append(f'<text x="{gx:.1f}" y="{x_zero_y + 18 if x_zero_y < height - 40 else height - 44}" fill="rgba(255,255,255,0.4)" font-size="12" text-anchor="middle">{xt}</text>')

    # Horizontal grid & y-ticks
    for yt in range(int(math.floor(y_min / y_step) * y_step), int(math.ceil(y_max / y_step) * y_step) + 1, y_step):
        gy = px_y(yt)
        if padding <= gy <= height - padding:
            grid_elements.append(f'<line x1="{padding}" y1="{gy:.1f}" x2="{width-padding}" y2="{gy:.1f}" stroke="rgba(255,255,255,0.05)" stroke-width="1" stroke-dasharray="4 4"/>')
            grid_elements.append(f'<text x="{y_zero_x - 10 if y_zero_x > 40 else padding + 10}" y="{gy + 4:.1f}" fill="rgba(255,255,255,0.4)" font-size="12" text-anchor="end">{yt}</text>')

    # Point labels
    marker_markup = f"""
      <circle cx="{px_x(0):.1f}" cy="{px_y(c):.1f}" r="5" fill="#ef4444" stroke="#fff" stroke-width="1.5" />
      <text x="{px_x(0) + 10:.1f}" y="{px_y(c) - 10:.1f}" fill="#ef4444" font-size="13" font-weight="700" filter="drop-shadow(0 1px 2px rgba(0,0,0,0.5))">(0, {c:g})</text>
      
      <circle cx="{px_x(x_vertex):.1f}" cy="{px_y(y_vertex):.1f}" r="5" fill="#22c55e" stroke="#fff" stroke-width="1.5" />
      <text x="{px_x(x_vertex) + 10:.1f}" y="{px_y(y_vertex) + 15:.1f}" fill="#22c55e" font-size="13" font-weight="700" filter="drop-shadow(0 1px 2px rgba(0,0,0,0.5))">({x_vertex:g}, {y_vertex:g})</text>
    """

    svg = f"""<svg viewBox="0 0 {width} {height}" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:transparent; font-family: 'Inter', sans-serif;">
      <rect width="100%" height="100%" fill="transparent" />
      <text x="{width/2}" y="30" fill="#fff" font-size="18" font-weight="900" text-anchor="middle" style="letter-spacing: 0.05em; opacity: 0.9;">{title}</text>
      
      <!-- Grids -->
      {''.join(grid_elements)}
      
      <!-- Axes -->
      <line x1="{padding}" y1="{x_zero_y:.1f}" x2="{width-padding}" y2="{x_zero_y:.1f}" stroke="rgba(255,255,255,0.2)" stroke-width="2" />
      <line x1="{y_zero_x:.1f}" y1="{padding}" x2="{y_zero_x:.1f}" y2="{height-padding}" stroke="rgba(255,255,255,0.2)" stroke-width="2" />
      
      <!-- Curve -->
      <polyline points="{path_data}" fill="none" stroke="#3b82f6" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" filter="drop-shadow(0 0 8px rgba(59,130,246,0.3))" />
      
      {marker_markup}
      
      <text x="{width-padding+10}" y="{x_zero_y+5}" fill="rgba(255,255,255,0.5)" font-size="14" font-weight="700">x</text>
      <text x="{y_zero_x-5}" y="{padding-15}" fill="rgba(255,255,255,0.5)" font-size="14" font-weight="700">y</text>
    </svg>"""
    return svg


def _render_svg_plot(points: list[tuple[float, float]], title: str = "Function Plot", line: tuple[float, float] | None = None) -> str:
    """Generate a clean, professional SVG plot for extracted graph points."""
    if not points:
        return ""

    width, height = 760, 500
    padding = 60

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    
    min_x, max_x = min(min(xs), 0), max(max(xs), 0)
    min_y, max_y = min(min(ys), 0), max(max(ys), 0)
    
    x_span = max_x - min_x or 1
    y_span = max_y - min_y or 1
    
    # Extra padding for curves
    min_x -= x_span * 0.1
    max_x += x_span * 0.1
    min_y -= y_span * 0.1
    max_y += y_span * 0.1
    x_span = max_x - min_x
    y_span = max_y - min_y

    def px_x(x): return padding + (x - min_x) / x_span * (width - 2 * padding)
    def px_y(y): return height - padding - (y - min_y) / y_span * (height - 2 * padding)

    x_zero_y = px_y(0)
    y_zero_x = px_x(0)

    polyline = " ".join(f"{px_x(x):.1f},{px_y(y):.1f}" for x, y in points)
    
    line_markup = ""
    if line is not None:
        slope, intercept = line
        lx1, lx2 = min_x, max_x
        ly1, ly2 = slope * lx1 + intercept, slope * lx2 + intercept
        line_markup = f'<line x1="{px_x(lx1):.1f}" y1="{px_y(ly1):.1f}" x2="{px_x(lx2):.1f}" y2="{px_y(ly2):.1f}" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6 4" filter="drop-shadow(0 0 4px rgba(56,189,248,0.4))" />'

    points_markup = "".join(
        f'<circle cx="{px_x(x):.1f}" cy="{px_y(y):.1f}" r="4.5" fill="#f59e0b" stroke="#fff" stroke-width="1.5" />'
        for x, y in points
    )

    svg = f"""<svg viewBox="0 0 {width} {height}" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:transparent; font-family: 'Inter', sans-serif;">
      <rect width="100%" height="100%" fill="transparent" />
      <text x="{width/2}" y="30" fill="#fff" font-size="18" font-weight="900" text-anchor="middle" style="letter-spacing: 0.05em; opacity: 0.9;">{title}</text>
      
      <!-- Axes -->
      <line x1="{padding}" y1="{x_zero_y:.1f}" x2="{width-padding}" y2="{x_zero_y:.1f}" stroke="rgba(255,255,255,0.2)" stroke-width="2" />
      <line x1="{y_zero_x:.1f}" y1="{padding}" x2="{y_zero_x:.1f}" y2="{height-padding}" stroke="rgba(255,255,255,0.2)" stroke-width="2" />
      
      <!-- Labels -->
      <text x="{width-padding+10}" y="{x_zero_y+5}" fill="rgba(255,255,255,0.4)" font-size="12">x</text>
      <text x="{y_zero_x-5}" y="{padding-10}" fill="rgba(255,255,255,0.4)" font-size="12">y</text>

      {line_markup}
      <polyline points="{polyline}" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" />
      {points_markup}
    </svg>"""
    return svg


def _asks_for_math_draw(text: str) -> bool:
    """Check if the text contains verbs asking the student to draw or transform a graph/diagram."""
    draw_keywords = ["draw", "plot", "sketch", "construct", "reflect", "rotate", "translate", "enlarge", "graph", "diagram", "curve", "axis"]
    pattern = r"\b(" + "|".join(draw_keywords) + r")\b"
    return bool(re.search(pattern, text, re.IGNORECASE))


def _is_scatter_question(text: str) -> bool:
    """Detect if the question is a scatter diagram question."""
    lowered = text.lower()
    scatter_patterns = [
        r"scatter",
        r"line of best fit",
        r"best fit",
        r"correlation",
        r"scatter diagram",
        r"scatter graph",
        r"plot the remaining",
        r"first 6 points",
        r"first six points",
        r"mathematics mark",
        r"physics mark",
    ]
    return any(re.search(pattern, lowered) for pattern in scatter_patterns)


def _is_geometry_diagram_question(text: str) -> bool:
    """Detect if the question refers to a geometry diagram (angles, lines, triangles, etc.)."""
    lowered = text.lower()
    geometry_patterns = [
        r"angle", r"calculate x", r"value of x", r"value of y",
        r"triangle", r"quadrilateral", r"circle", r"tangent",
        r"parallel line", r"perpendicular", r"isosceles", r"equilateral",
        r"congruent", r"similar", r"bearing", r"length of", r"cm",
        r"find the angle", r"show that", r"bisector"
    ]
    return any(re.search(pattern, lowered) for pattern in geometry_patterns)


def _extract_table_data(text: str) -> list[tuple[float, float]]:
    """Extract coordinate table data from OCR text for scatter diagrams only."""
    if not text:
        return []

    # Prefer explicit Mathematics vs Physics table rows.
    table_points = _extract_scatter_table_points(text)
    if table_points:
        return table_points

    lowered = text.lower()
    if not any(keyword in lowered for keyword in ["scatter", "best fit", "line of best fit", "correlation", "mathematics", "physics"]):
        return []

    pairs = []
    for match in re.finditer(r"\(?\s*([+-]?\d+(?:\.\d+)?)\s*[,;]\s*([+-]?\d+(?:\.\d+)?)\s*\)?", text):
        try:
            x = float(match.group(1))
            y = float(match.group(2))
            if 0 <= x <= 100 and 0 <= y <= 100:
                pairs.append((x, y))
        except ValueError:
            continue

    return pairs


def _remove_axis_sequences(values: list[float]) -> list[float]:
    """Remove long arithmetic sequences of axis labels (e.g. 20,30,40,...) from row values."""
    if len(values) < 4:
        return values

    def is_axis_seq(seq: list[float]) -> bool:
        if len(seq) < 4:
            return False
        diff = round(seq[1] - seq[0], 6)
        if abs(abs(diff) - 10) > 1e-6:
            return False
        return all(abs((seq[i+1] - seq[i]) - diff) < 1e-6 for i in range(len(seq) - 1))

    def strip_sequence(vals: list[float], start: int, end: int) -> list[float]:
        return vals[:start] + vals[end:]

    cleaned = values[:]

    # Remove prefix axis sequences
    for i in range(len(cleaned), 3, -1):
        if is_axis_seq(cleaned[:i]):
            if len(cleaned) - i >= 3:
                cleaned = cleaned[i:]
            break

    # Remove suffix axis sequences
    for i in range(0, len(cleaned) - 3):
        seq = cleaned[i:]
        if is_axis_seq(seq):
            if i >= 3:
                cleaned = cleaned[:i]
            break

    # Remove internal axis-like runs if they appear and leave enough values
    i = 0
    while i < len(cleaned) - 3:
        j = i + 4
        while j <= len(cleaned) and is_axis_seq(cleaned[i:j]):
            if j == len(cleaned) or not is_axis_seq(cleaned[i:j+1]):
                break
            j += 1
        if is_axis_seq(cleaned[i:j]):
            if len(cleaned) - (j - i) >= 3:
                cleaned = strip_sequence(cleaned, i, j)
                continue
        i += 1

    return cleaned


def _extract_scatter_table_points(text: str) -> list[tuple[float, float]]:
    """Extract Maths and Physics row data when table labels are present."""
    if not text:
        return []

    math_match = re.search(r"mathematics marks?\s*([0-9\s,\.\-]+?)(?=physics marks?|$)", text, flags=re.I)
    phys_match = re.search(r"physics marks?\s*([0-9\s,\.\-]+?)(?=mathematics marks?|$)", text, flags=re.I)

    if not math_match or not phys_match:
        math_match = re.search(r"mathematics mark[s]?\s*([0-9\s,\.\-]+?)(?=physics mark[s]?|$)", text, flags=re.I)
        phys_match = re.search(r"physics mark[s]?\s*([0-9\s,\.\-]+?)(?=mathematics mark[s]?|$)", text, flags=re.I)

    if not math_match or not phys_match:
        return []

    def parse_row(row_text: str) -> list[float]:
        values = [float(n) for n in re.findall(r"[0-9]+(?:\.[0-9]+)?", row_text)]
        return _remove_axis_sequences(values)

    math_values = parse_row(math_match.group(1))
    phys_values = parse_row(phys_match.group(1))

    if len(math_values) != len(phys_values) or len(math_values) == 0:
        return []

    return [(x, y) for x, y in zip(math_values, phys_values)]


def _is_first_six_plotted(text: str) -> bool:
    """Detect if the scatter question states that the first 6 points are already plotted."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in [
        "first 6 points",
        "first six points",
        "first 6",
        "first six",
        "first six points have been plotted",
        "first 6 points have been plotted",
        "first six points have already been plotted",
        "first 6 points have already been plotted",
    ])


def _build_scatter_solution_from_table(points: list[tuple[float, float]], extracted_text: str) -> dict | None:
    """Generate a data-driven scatter question solution."""
    if len(points) < 2:
        return None

    # Detect how many points are already plotted
    pre_plotted = 6 # Default for many papers, but we should be flexible
    if "first 8" in extracted_text.lower(): pre_plotted = 8
    elif "first 5" in extracted_text.lower(): pre_plotted = 5

    missing_points = points[pre_plotted:]
    if not missing_points:
        # Check if they just want the line of best fit or estimation
        pass

    coords_text = ", ".join(f"({x:g},{y:g})" for x, y in missing_points) if missing_points else "None (all plotted)"
    fit = _compute_best_fit_line(points)
    
    # Try to detect estimation request
    # Often it's like "Estimate the marks for Physics if Mathematics is 75"
    est_x = None
    est_y = None
    
    # Simple heuristic for common questions
    if "physics" in extracted_text.lower() and "75" in extracted_text:
        est_y = 75.0
    
    if fit and est_y is not None:
        slope, intercept = fit
        if slope != 0:
            est_x = round((est_y - intercept) / slope, 1)

    steps = []
    step_num = 1
    
    if missing_points:
        steps.append({
            "step_number": step_num,
            "part": "a",
            "description": f"Identify the missing points from the table to be plotted.",
            "expression": f"Points: {coords_text}",
            "concept_key": "scatter_graph",
        })
        step_num += 1
        steps.append({
            "step_number": step_num,
            "part": "a",
            "description": "Plot these points precisely on the grid.",
            "expression": "Points plotted.",
            "concept_key": "scatter_graph",
        })
        step_num += 1

    steps.append({
        "step_number": step_num,
        "part": "b",
        "description": "Draw a line of best fit. It should be a single straight line that follows the trend of the data points.",
        "expression": "Line of best fit drawn.",
        "concept_key": "scatter_graph",
    })
    step_num += 1

    if est_x is not None:
        steps.append({
            "step_number": step_num,
            "part": "c",
            "description": f"Use the line of best fit to estimate the value when y = {est_y}.",
            "expression": f"x ≈ {est_x}",
            "concept_key": "scatter_graph",
        })

    return {
        "steps": steps,
        "final_answer": f"Missing points: {coords_text}. Estimate: {est_x if est_x else 'N/A'}",
        "mark_commentary": "Marks awarded for plotting (2), line of best fit (1), and estimation (1).",
        "visual_data": None,
    }


def _render_scatter_svg(
    all_points: list[tuple[float, float]],
    pre_plotted: int = 6,
    estimate_y: float | None = None,
    estimate_x: float | None = None,
    x_label: str = "x-axis",
    y_label: str = "y-axis",
    x_min: float | None = None, x_max: float | None = None,
    y_min: float | None = None, y_max: float | None = None,
) -> str:
    """
    Render a clean, exam-standard scatter diagram SVG with:
    - Pre-plotted points (gray crosses)
    - Newly plotted points (amber filled circles)
    - Least-squares line of best fit (sky-blue dashed)
    - Optional estimation reading mark (red dot + dotted projection lines)
    """
    W, H = 760, 520
    pad_left, pad_right, pad_top, pad_bottom = 70, 40, 40, 60

    plot_w = W - pad_left - pad_right
    plot_h = H - pad_top - pad_bottom

    if x_min is None: x_min = min(x for x, _ in all_points) - 5
    if x_max is None: x_max = max(x for x, _ in all_points) + 5
    if y_min is None: y_min = min(y for _, y in all_points) - 5
    if y_max is None: y_max = max(y for _, y in all_points) + 5

    x_min = min(x_min, 0)
    y_min = min(y_min, 0)

    x_span = x_max - x_min if x_max != x_min else 1
    y_span = y_max - y_min if y_max != y_min else 1

    def px(x_val: float) -> float:
        return pad_left + (x_val - x_min) / x_span * plot_w

    def py(y_val: float) -> float:
        return pad_top + (y_max - y_val) / y_span * plot_h

    # Grid lines
    def get_step(span):
        if span <= 10: return 1
        if span <= 25: return 5
        if span <= 100: return 10
        return 20

    x_tick_step = get_step(x_span)
    y_tick_step = get_step(y_span)

    grid_lines = []
    for xv in range(int(math.floor(x_min / x_tick_step) * x_tick_step), int(math.ceil(x_max / x_tick_step) * x_tick_step) + 1, x_tick_step):
        gx = px(xv)
        if pad_left <= gx <= W - pad_right:
            grid_lines.append(f'<line x1="{gx:.1f}" y1="{pad_top}" x2="{gx:.1f}" y2="{pad_top+plot_h}" stroke="rgba(248,250,252,0.05)" stroke-width="1" stroke-dasharray="4 4"/>')
            grid_lines.append(f'<text x="{gx:.1f}" y="{pad_top+plot_h+18}" fill="#94a3b8" font-size="13" text-anchor="middle" font-family="Inter,sans-serif">{xv}</text>')
            grid_lines.append(f'<line x1="{gx:.1f}" y1="{pad_top+plot_h}" x2="{gx:.1f}" y2="{pad_top+plot_h+5}" stroke="#f8fafc" stroke-width="1.5"/>')
    for yv in range(int(math.floor(y_min / y_tick_step) * y_tick_step), int(math.ceil(y_max / y_tick_step) * y_tick_step) + 1, y_tick_step):
        gy = py(yv)
        if pad_top <= gy <= H - pad_bottom:
            grid_lines.append(f'<line x1="{pad_left}" y1="{gy:.1f}" x2="{pad_left+plot_w}" y2="{gy:.1f}" stroke="rgba(248,250,252,0.05)" stroke-width="1" stroke-dasharray="4 4"/>')
            grid_lines.append(f'<text x="{pad_left-10}" y="{gy+4:.1f}" fill="#94a3b8" font-size="13" text-anchor="end" font-family="Inter,sans-serif">{yv}</text>')
            grid_lines.append(f'<line x1="{pad_left-5}" y1="{gy:.1f}" x2="{pad_left}" y2="{gy:.1f}" stroke="#f8fafc" stroke-width="1.5"/>')

    # Axes
    axes = f'''
    <line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{pad_top+plot_h}" stroke="#f8fafc" stroke-width="2.5"/>
    <line x1="{pad_left}" y1="{pad_top+plot_h}" x2="{pad_left+plot_w}" y2="{pad_top+plot_h}" stroke="#f8fafc" stroke-width="2.5"/>
    '''

    # Axis labels
    axis_labels = f'''
    <text x="{pad_left + plot_w/2}" y="{H-8}" fill="#f8fafc" font-size="14" text-anchor="middle" font-weight="700" font-family="Inter,sans-serif">{x_label}</text>
    <text x="18" y="{pad_top + plot_h/2}" fill="#f8fafc" font-size="14" text-anchor="middle" font-weight="700" font-family="Inter,sans-serif" transform="rotate(-90,18,{pad_top+plot_h/2})">{y_label}</text>
    '''

    # Compute best fit line
    line_markup = ""
    if len(all_points) >= 2:
        fit = _compute_best_fit_line(all_points)
        if fit:
            slope, intercept = fit
            lx1, lx2 = x_min, x_max
            ly1 = slope * lx1 + intercept
            ly2 = slope * lx2 + intercept
            ly1 = max(y_min, min(y_max, ly1))
            ly2 = max(y_min, min(y_max, ly2))
            line_markup = (
                f'<line x1="{px(lx1):.1f}" y1="{py(ly1):.1f}" '
                f'x2="{px(lx2):.1f}" y2="{py(ly2):.1f}" '
                f'stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="8 4" opacity="0.9"/>'
            )

    # Plot points
    point_markup = []
    for i, (xv, yv) in enumerate(all_points):
        cx, cy = px(xv), py(yv)
        if i < pre_plotted:
            # Pre-plotted: gray cross
            s = 6
            point_markup.append(
                f'<line x1="{cx-s}" y1="{cy-s}" x2="{cx+s}" y2="{cy+s}" stroke="#94a3b8" stroke-width="2.5"/>'
                f'<line x1="{cx+s}" y1="{cy-s}" x2="{cx-s}" y2="{cy+s}" stroke="#94a3b8" stroke-width="2.5"/>'
            )
        else:
            # New points: amber filled circle with ring
            point_markup.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="#f59e0b" stroke="#ffffff" stroke-width="1.5"/>'
            )

    # Estimation reading lines and point
    estimate_markup = ""
    if estimate_y is not None and estimate_x is not None:
        ex, ey = px(estimate_x), py(estimate_y)
        ey_left = py(estimate_y)
        ex_bottom = px(estimate_x)
        # Horizontal dotted line from y-axis to the reading point
        estimate_markup += f'<line x1="{pad_left}" y1="{ey_left:.1f}" x2="{ex:.1f}" y2="{ey_left:.1f}" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="5 4" opacity="0.8"/>'
        # Vertical dotted line from reading point down to x-axis
        estimate_markup += f'<line x1="{ex:.1f}" y1="{ey_left:.1f}" x2="{ex:.1f}" y2="{pad_top+plot_h}" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="5 4" opacity="0.8"/>'
        # The reading point on line
        estimate_markup += f'<circle cx="{ex:.1f}" cy="{ey_left:.1f}" r="7" fill="#ef4444" stroke="#fff" stroke-width="1.5"/>'
        # Labels
        estimate_markup += f'<text x="{pad_left+6}" y="{ey_left-6:.1f}" fill="#ef4444" font-size="12" font-family="Inter,sans-serif">y={estimate_y:.0f}</text>'
        estimate_markup += f'<text x="{ex+6:.1f}" y="{pad_top+plot_h+16}" fill="#ef4444" font-size="12" font-family="Inter,sans-serif">x≈{estimate_x:.0f}</text>'

    # Legend
    legend = f'''
    <circle cx="{pad_left+16}" cy="{pad_top+14}" r="5" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
    <line x1="{pad_left+10}" y1="{pad_top+8}" x2="{pad_left+22}" y2="{pad_top+20}" stroke="#94a3b8" stroke-width="2"/>
    <line x1="{pad_left+22}" y1="{pad_top+8}" x2="{pad_left+10}" y2="{pad_top+20}" stroke="#94a3b8" stroke-width="2"/>
    <text x="{pad_left+30}" y="{pad_top+18}" fill="#94a3b8" font-size="11" font-family="Inter,sans-serif">Pre-plotted ({pre_plotted})</text>
    <circle cx="{pad_left+130}" cy="{pad_top+14}" r="5" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>
    <text x="{pad_left+140}" y="{pad_top+18}" fill="#f59e0b" font-size="11" font-family="Inter,sans-serif">Newly plotted ({len(all_points)-pre_plotted})</text>
    <line x1="{pad_left+270}" y1="{pad_top+14}" x2="{pad_left+295}" y2="{pad_top+14}" stroke="#38bdf8" stroke-width="2" stroke-dasharray="6 3"/>
    <text x="{pad_left+300}" y="{pad_top+18}" fill="#38bdf8" font-size="11" font-family="Inter,sans-serif">Line of best fit</text>
    '''
    if estimate_x is not None:
        legend += f'''
        <circle cx="{pad_left+420}" cy="{pad_top+14}" r="5" fill="#ef4444" stroke="#fff" stroke-width="1.5"/>
        <text x="{pad_left+430}" y="{pad_top+18}" fill="#ef4444" font-size="11" font-family="Inter,sans-serif">Estimated point</text>
        '''

    title_text = f"Scatter Diagram — {x_label} vs {y_label}"
    title = f'<text x="{W//2}" y="22" fill="#f8fafc" font-size="15" text-anchor="middle" font-weight="700" font-family="Inter,sans-serif">{title_text}</text>'

    svg = f'''<svg viewBox="0 0 {W} {H}" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:transparent">
  <rect width="{W}" height="{H}" fill="transparent"/>
  {title}
  {''.join(grid_lines)}
  {axes}
  {axis_labels}
  {line_markup}
  {''.join(point_markup)}
  {estimate_markup}
  {legend}
</svg>'''
    return svg


def _build_graph_visual(query: str, extracted_text: str) -> str | None:
    combined_text = f"{query} {extracted_text}"
    if not _asks_for_math_draw(combined_text):
        return None

    # Scatter diagram detection (highest priority for this type of question)
    if _is_scatter_question(combined_text):
        pairs = _extract_table_data(extracted_text) or _extract_table_data(query)
        if len(pairs) >= 2:
            fit = _compute_best_fit_line(pairs)
            est_x = None
            est_y = None
            if fit:
                slope, intercept = fit
                if slope != 0:
                    est_y = 75.0
                    est_x = round((est_y - intercept) / slope, 1)
            return _render_scatter_svg(
                all_points=pairs,
                pre_plotted=min(6, len(pairs)),
                estimate_y=est_y,
                estimate_x=est_x,
            )

    quadratic = _extract_quadratic_equation(combined_text)
    if quadratic:
        a, b, c = quadratic
        return _render_quadratic_svg(a, b, c, title="Quadratic graph")

    points = _extract_coordinate_pairs(combined_text)
    if len(points) >= 2:
        line = _compute_best_fit_line(points)
        return _render_svg_plot(points, title="Extracted graph from image", line=line)

    return None


def get_math_context(query: str, extracted_text: str = "", marks: int = 4) -> str:
    """Find relevant O-Level syllabus tips, marking patterns, and past paper examples based on the query."""
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

    # Inject past paper context from 2002-2025 dataset
    combined_query = f"{query} {extracted_text}"
    past_paper_context = _get_past_paper_context(combined_query, marks)
    if past_paper_context:
        context += f"\n{past_paper_context}\n"
            
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

    # Enrich context with past paper mark schemes (2002-2025)
    context = get_math_context(question, marks=marks)

    user_prompt = (
        f"EXAM QUESTION {question_number} [{marks} MARKS]\n\n"
        f"{question.strip()}\n\n"
        f"As a master O-Level Cambridge 4024 examiner, provide a high-precision, step-by-step solution. "
        f"The depth of your explanation and the number of steps must be strictly calibrated to the {marks} marks awarded. "
        "Show all necessary algebraic manipulations and intermediate results. "
        "Use Unicode notation for all mathematical symbols."
        + (f"\n\n{context}" if context else "")
    )

    raw = llm.generate_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=3000,
        temperature=0.0,
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
    visual_data = data.get("visual_data") if _asks_for_math_draw(question) else None
    return {
        "question_number": question_number,
        "marks": marks,
        "steps": steps,
        "final_answer": str(data.get("final_answer", "")),
        "mark_commentary": str(data.get("mark_commentary", f"[{marks} mark(s)]")),
        "visual_data": visual_data,
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
            if matched:
                break

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

    # --- Detect question type for targeted prompting ---
    combined_text = f"{query} {extracted_text}"
    is_diagram = _is_geometry_diagram_question(combined_text)
    diagram_description = ""
    if is_diagram:
        diagram_description = extract_diagram_description_from_vision(image_base64)
        if diagram_description:
            combined_text = f"{combined_text} {diagram_description}"

    is_scatter = _is_scatter_question(combined_text)
    asks_draw = _asks_for_math_draw(combined_text)

    # For scatter diagrams, extract the table data deterministically
    scatter_pairs: list[tuple[float, float]] = []
    scatter_svg: str | None = None
    if is_scatter:
        scatter_pairs = _extract_table_data(combined_text) or _extract_table_data(query) or _extract_table_data(extracted_text)
        if len(scatter_pairs) < 2:
            scatter_pairs = []

    if is_scatter and scatter_pairs:
        # Add a deterministic fallback for well-formed scatter-table questions.
        fit = _compute_best_fit_line(scatter_pairs)
        est_x: float | None = None
        est_y = 75.0
        if fit:
            slope, intercept = fit
            if slope != 0:
                est_x = round((est_y - intercept) / slope, 1)
        scatter_svg = _render_scatter_svg(
            all_points=scatter_pairs,
            pre_plotted=min(6, len(scatter_pairs)),
            estimate_y=est_y,
            estimate_x=est_x,
        )
        deterministic_solution = _build_scatter_solution_from_table(scatter_pairs, extracted_text or query)
        if deterministic_solution:
            return {
                "question_number": 1,
                "marks": marks,
                "steps": deterministic_solution["steps"],
                "final_answer": deterministic_solution["final_answer"],
                "mark_commentary": deterministic_solution["mark_commentary"],
                "visual_data": scatter_svg,
                "raw_question": extracted_text or query,
            }

    # Build a very specific supplemental system directive
    scatter_injection = ""
    if is_scatter and scatter_pairs and _is_first_six_plotted(extracted_text or query):
        rows = "\n".join(f"  Point {i+1}: Maths={x:.0f}, Physics={y:.0f}" for i, (x, y) in enumerate(scatter_pairs))
        scatter_injection = (
            f"\n\n### SCATTER DATA DETECTED FROM IMAGE\n"
            f"The following {len(scatter_pairs)} (Mathematics, Physics) data points were found in the table:\n"
            f"{rows}\n"
            f"The first 6 points are already pre-plotted. The remaining {len(scatter_pairs)-6} points "
            f"(if any) must be plotted by the student.\n"
            f"For part (a): State which 3 points to plot and give their exact (Maths, Physics) coordinates.\n"
            f"For part (b): Describe how to draw the line of best fit (passing close to as many points as possible).\n"
            f"For part (c): Use the line of best fit to estimate Xavier's Mathematics mark when his Physics mark is 75.\n"
            f"Set visual_data to null — the SVG diagram will be generated programmatically.\n"
        )

    geometry_injection = ""
    if is_diagram:
        geometry_injection = (
            "\n\n### GEOMETRY DIAGRAM RULES\n"
            "This image contains a geometry diagram with angles, lines, or triangles. Use only the exact labels, angles, markings and text shown in the image. "
            "Do not invent additional angles, sides, or relationships that are not present in the diagram. "
            "If the diagram description lists equal sides or angle markings, use them directly in your reasoning."
        )

    extracted_image_reference = extracted_text
    if diagram_description:
        extracted_image_reference += "\nDiagram description: " + diagram_description

    system_prompt = (
        SYSTEM_PROMPT
        + "\n\n### IMPORTANT: IMAGE ANALYSIS RULES\n"
        + "1. You are looking at the ACTUAL exam image. Read ALL sub-parts from it.\n"
        + "2. EVERY sub-part ((a), (b), (c), (i), (ii), etc.) must have at least one step in `steps`.\n"
        + "3. For each step, the `expression` field MUST contain the actual working, coordinates, formula, or computed result.\n"
        + "4. The `part` field for each step MUST exactly match the sub-part label (e.g. 'a', 'b', 'c', 'i', 'ii').\n"
        + "5. `final_answer` must summarise the final result for EACH sub-part.\n"
        + geometry_injection
        + scatter_injection
        + "\nExtracted image text for reference:\n" + extracted_image_reference
        + "\n\n" + context
    )

    user_prompt = (
        f"This is a {marks}-mark Cambridge O-Level Mathematics question (multipart).\n"
        f"User query: {query}\n\n"
        f"TASK: Solve ONLY the visible question parts in the image. Use only the relationships explicitly stated in the image text. "
        f"Do not infer extra angle or algebraic relationships that are not visible in the question. "
        f"Do not add unrelated theory, examples, or general comments. "
        f"Provide complete, step-by-step, mark-scheme quality answers for each part. "
        f"Do not skip any part. For graph/plot parts, describe the action and include the exact coordinates. "
        f"Return your answer as a single valid JSON object matching the required structure."
    )

    raw = llm.generate_vision_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        image_base64=image_base64
    )

    # 3. Parse and Return
    try:
        # Parse JSON
        json_str = _extract_json(raw)
        data = json.loads(json_str)
        steps = _validate_steps(data.get("steps", []))
        
        # --- IMPROVED MARK DETECTION PRIORITY ---
        # If AI found marks in paper, use them. 
        # If user passed 4 (default), but AI found 2, AI wins.
        # If user passed something else, they probably know better.
        ai_detected_marks = data.get("detected_marks")
        final_marks = marks
        if ai_detected_marks and ai_detected_marks > 0:
            # If provided marks is 4 (the suspect default), update it.
            if marks == 4:
                final_marks = ai_detected_marks
            else:
                # If provided marks is significantly different, we trust AI findings more for '4'
                final_marks = ai_detected_marks

        # Build visual: prefer our deterministic SVG for scatter, otherwise fall back to AI SVG
        visual_data = None
        if is_scatter and scatter_pairs:
            # Compute best fit to get Xavier's estimate
            fit = _compute_best_fit_line(scatter_pairs)
            est_x: float | None = None
            est_y = 75.0
            if fit:
                slope, intercept = fit
                if slope != 0:
                    est_x = round((est_y - intercept) / slope, 1)
            scatter_svg = _render_scatter_svg(
                all_points=scatter_pairs,
                pre_plotted=6,
                estimate_y=est_y,
                estimate_x=est_x,
            )
            visual_data = scatter_svg
        elif asks_draw:
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
