"""
weakness_analyzer.py
Core service for computing per-topic weakness scores and generating
practice question recommendations + LLM-powered study plans.
"""
import json
import math
import re
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Optional

from app.models.schemas import (
    EnhancedWeaknessResponse,
    PracticeQuestion,
    WeakArea,
)
from app.repositories.data_repository import DataRepository
from app.services.llm_service import LLMService
from app.utils.session_store import get_session_interactions

# ─── Topic Display Names ──────────────────────────────────────────────────────
TOPIC_DISPLAY_NAMES: dict[str, str] = {
    # Math
    "circle_theorems": "Circle Theorems",
    "simultaneous_equations": "Simultaneous Equations",
    "trigonometry": "Trigonometry",
    "quadratic_formula": "Quadratic Formula",
    "probability": "Probability & Statistics",
    "fractions": "Fractions",
    "percentages": "Percentages",
    "vectors": "Vectors",
    "matrix": "Matrices",
    "histogram": "Histograms",
    "linear_equations": "Linear Equations",
    "pythagoras": "Pythagoras Theorem",
    "sequences": "Sequences & Series",
    "indices": "Indices & Powers",
    "sine_rule": "Sine Rule",
    "cosine_rule": "Cosine Rule",
    "ratio": "Ratio & Proportion",
    "factorisation": "Factorisation",
    # History
    "allama_iqbal": "Allama Iqbal",
    "quaid_e_azam": "Quaid-e-Azam",
    "liaquat_ali_khan": "Liaquat Ali Khan",
    "partition_1947": "Partition of India (1947)",
    "lahore_resolution_1940": "Lahore Resolution (1940)",
    "simon_commission": "Simon Commission",
    "khilafat_movement": "Khilafat Movement",
    "war_of_independence_1857": "War of Independence (1857)",
    "sir_syed_ahmed_khan": "Sir Syed Ahmed Khan",
    # Geography
    "map_reading": "Map Reading Skills",
    "rivers_and_drainage": "Rivers & Drainage Systems",
    "climate_and_rainfall": "Climate & Rainfall Patterns",
    "population": "Population Studies",
    "agriculture_and_land_use": "Agriculture & Land Use",
    "transport": "Transport Networks",
    "topography": "Topography",
    "natural_disasters": "Natural Disasters",
    # Economics
    "demand_and_supply": "Demand & Supply",
    "price_elasticity": "Price Elasticity",
    "inflation": "Inflation",
    "unemployment": "Unemployment",
    "gdp_and_growth": "GDP & Economic Growth",
    "market_structures": "Market Structures",
    "balance_of_payments": "Balance of Payments",
}

# ─── Keyword → Topic Mapping ──────────────────────────────────────────────────
KEYWORD_TOPIC_MAP: dict[str, str] = {
    # Math
    "circle theorem": "circle_theorems",
    "angle in semicircle": "circle_theorems",
    "tangent": "circle_theorems",
    "simultaneous": "simultaneous_equations",
    "quadratic": "quadratic_formula",
    "trigon": "trigonometry",
    "sin": "trigonometry",
    "cos": "trigonometry",
    "tan": "trigonometry",
    "sine rule": "sine_rule",
    "cosine rule": "cosine_rule",
    "probability": "probability",
    "histogram": "histogram",
    "matrix": "matrix",
    "vector": "vectors",
    "fraction": "fractions",
    "percentage": "percentages",
    "pythagoras": "pythagoras",
    "indices": "indices",
    "sequence": "sequences",
    "ratio": "ratio",
    "factoris": "factorisation",
    "linear equation": "linear_equations",
    # History
    "iqbal": "allama_iqbal",
    "jinnah": "quaid_e_azam",
    "quaid": "quaid_e_azam",
    "liaquat": "liaquat_ali_khan",
    "partition": "partition_1947",
    "lahore resolution": "lahore_resolution_1940",
    "simon commission": "simon_commission",
    "khilafat": "khilafat_movement",
    "1857": "war_of_independence_1857",
    "war of independence": "war_of_independence_1857",
    "sir syed": "sir_syed_ahmed_khan",
    # Geography
    "rainfall": "climate_and_rainfall",
    "climate": "climate_and_rainfall",
    "river": "rivers_and_drainage",
    "drainage": "rivers_and_drainage",
    "population": "population",
    "map": "map_reading",
    "contour": "map_reading",
    "grid reference": "map_reading",
    "agriculture": "agriculture_and_land_use",
    "transport": "transport",
    "earthquake": "natural_disasters",
    "flood": "natural_disasters",
    # Economics
    "demand": "demand_and_supply",
    "supply": "demand_and_supply",
    "elasticity": "price_elasticity",
    "inflation": "inflation",
    "gdp": "gdp_and_growth",
    "unemployment": "unemployment",
    "market structure": "market_structures",
    "balance of payment": "balance_of_payments",
}


def classify_topic(question_text: str, subject: str) -> str:
    """Fast keyword-based topic classification. Returns a topic key."""
    text_lower = question_text.lower()
    for keyword, topic in KEYWORD_TOPIC_MAP.items():
        if keyword in text_lower:
            return topic
    return f"{subject}_general"


def extract_marks_from_response(response_text: str, marks_available: int) -> int:
    """
    Parse examiner band from LLM response to estimate marks obtained.
    Looks for the pattern written by history_routes.py STEP 6 & 7:
        [EXAMINER AUDIT: 11/14]
    """
    pattern = r"\[EXAMINER AUDIT:\s*(\d+)/(\d+)\]"
    match = re.search(pattern, response_text)
    if match:
        return int(match.group(1))

    # Band-based fallback estimation
    text_lower = response_text.lower()
    if "l4" in text_lower:
        return int(marks_available * 0.93)
    if "l3" in text_lower:
        return int(marks_available * 0.75)
    if "l2" in text_lower:
        return int(marks_available * 0.55)
    return int(marks_available * 0.30)   # L1 default


# ─── Core Analyzer ────────────────────────────────────────────────────────────

class WeaknessAnalyzer:
    def __init__(self, llm_service: LLMService, data_repo: DataRepository):
        self.llm = llm_service
        self.repo = data_repo

    # ── Scoring ──────────────────────────────────────────────────────────────

    def compute_weakness_scores(
        self,
        interactions: list,
        decay_lambda: float = 0.1,
    ) -> dict[str, dict]:
        """
        Compute per-topic weakness scores using a temporal exponential decay model.

        Score formula (per interaction i):
            contribution = error_ratio * decay(days_ago) * mark_weight

        where:
            error_ratio  = (marks_available - marks_obtained) / marks_available
            decay        = exp(-lambda * days_since_interaction)
            mark_weight  = marks_available / 14  (normalise to [0,1])
        """
        now = datetime.now()
        topic_data: dict[str, dict] = defaultdict(
            lambda: {
                "score": 0.0,
                "max_score": 0.0,
                "attempts": 0,
                "last_attempted": None,
                "subject": "unknown",
                "normalized_score": 0.0,
            }
        )

        for ix in interactions:
            topic = ix.get("topic") or "general"
            marks_avail = max(1, ix.get("marks_available", 4))
            marks_got = ix.get("marks_obtained")

            # Skip unscored interactions — they inform topic breadth but not weakness
            if marks_got is None:
                topic_data[topic]["attempts"] += 1
                topic_data[topic]["subject"] = ix.get("subject", "unknown")
                ts = ix.get("timestamp")
                if ts and (not topic_data[topic]["last_attempted"] or ts > topic_data[topic]["last_attempted"]):
                    topic_data[topic]["last_attempted"] = ts
                continue

            ts_str = ix.get("timestamp", datetime.now().isoformat())
            try:
                ts = datetime.fromisoformat(ts_str)
            except (ValueError, TypeError):
                ts = now

            days_ago = max(0, (now - ts).days)
            decay = math.exp(-decay_lambda * days_ago)
            mark_weight = marks_avail / 14.0

            error = max(0, marks_avail - marks_got)
            error_ratio = error / marks_avail

            td = topic_data[topic]
            td["score"] += error_ratio * decay * mark_weight
            td["max_score"] += decay * mark_weight
            td["attempts"] += 1
            td["subject"] = ix.get("subject", "unknown")
            if not td["last_attempted"] or ts_str > td["last_attempted"]:
                td["last_attempted"] = ts_str

        # Normalise
        result: dict[str, dict] = {}
        for topic, data in topic_data.items():
            norm = data["score"] / data["max_score"] if data["max_score"] > 0 else 0.0
            result[topic] = {**data, "normalized_score": round(norm, 3)}

        return dict(sorted(result.items(), key=lambda x: -x[1]["normalized_score"]))

    def get_weak_areas(
        self, scores: dict, threshold: float = 0.35
    ) -> list[WeakArea]:
        """Return weak topics above the score threshold, capped at 8."""
        weak: list[WeakArea] = []
        for topic, data in scores.items():
            if data["normalized_score"] >= threshold:
                weak.append(
                    WeakArea(
                        topic=topic,
                        subject=data["subject"],
                        weakness_score=data["normalized_score"],
                        attempts=data["attempts"],
                        last_attempted=data.get("last_attempted"),
                        display_name=TOPIC_DISPLAY_NAMES.get(
                            topic, topic.replace("_", " ").title()
                        ),
                    )
                )
        return weak[:8]

    # ── Recommendations ───────────────────────────────────────────────────────

    def get_practice_questions(
        self, weak_areas: list[WeakArea]
    ) -> list[PracticeQuestion]:
        """Find relevant past-paper questions for the top-5 weak areas."""
        math_papers = self.repo.get_math_past_papers_data()
        econ_papers = self.repo.get_economics_past_papers_data()
        history_data = self.repo.get_history_data()

        recommendations: list[PracticeQuestion] = []

        for area in weak_areas[:5]:
            candidates = self._search_past_papers(
                area.topic, area.subject, math_papers, econ_papers, history_data
            )
            for q in candidates[:2]:
                recommendations.append(
                    PracticeQuestion(
                        question_id=str(uuid.uuid4()),
                        subject=area.subject,
                        topic=area.topic,
                        question_text=str(q.get("question", "Practice this topic."))[:300],
                        marks=int(q.get("marks", 4)),
                        year=str(q.get("year", "")),
                        difficulty=self._estimate_difficulty(int(q.get("marks", 4))),
                        why_recommended=(
                            f"You scored below average on '{area.display_name}' "
                            f"across {area.attempts} attempt(s). "
                            f"Weakness score: {int(area.weakness_score * 100)}%."
                        ),
                    )
                )

        return recommendations

    def _search_past_papers(
        self,
        topic: str,
        subject: str,
        math_papers: dict,
        econ_papers: dict,
        history_data: dict,
    ) -> list[dict]:
        """Search past-paper datasets for questions matching the topic keywords."""
        topic_words = set(topic.replace("_", " ").split())
        results: list[dict] = []

        if subject == "math" and math_papers:
            for year, year_data in math_papers.get("past_papers", {}).items():
                for session_data in year_data.values():
                    for paper_key in ("paper_1", "paper_2"):
                        for entry in session_data.get(paper_key, {}).get("mark_scheme", []):
                            q_lower = entry.get("question", "").lower()
                            if any(w in q_lower for w in topic_words if len(w) > 3):
                                results.append({**entry, "year": year})

        elif subject == "economics" and econ_papers:
            for year, year_data in econ_papers.get("past_papers", {}).items():
                for session in year_data.values():
                    for q in session.get("questions", []):
                        q_lower = q.get("question", "").lower()
                        if any(w in q_lower for w in topic_words if len(w) > 3):
                            results.append({**q, "year": year})

        elif subject == "history" and history_data:
            for topic_key, items in history_data.items():
                if not isinstance(items, list):
                    continue
                for item in items:
                    q_lower = str(item).lower()
                    if any(w in q_lower for w in topic_words if len(w) > 3):
                        results.append({"question": str(item)[:200], "marks": 4})

        return results[:6]

    @staticmethod
    def _estimate_difficulty(marks: int) -> str:
        if marks <= 3:
            return "easy"
        if marks <= 7:
            return "medium"
        return "hard"

    # ── LLM Study Plan ────────────────────────────────────────────────────────

    def generate_improvement_plan(
        self,
        weak_areas: list[WeakArea],
        interactions: list,
    ) -> tuple[str, str]:
        """Generate a personalised improvement plan and performance summary via LLM."""
        weak_list = (
            ", ".join(f"{a.display_name} ({a.subject})" for a in weak_areas[:5])
            or "No specific weaknesses detected yet — keep practising!"
        )
        subjects_tried = list({ix.get("subject", "unknown") for ix in interactions})
        total = len(interactions)

        prompt = f"""You are a Cambridge O-Level Academic Advisor for Gradiant AI.

STUDENT DATA:
- Total questions attempted: {total}
- Subjects studied: {', '.join(subjects_tried) if subjects_tried else 'None yet'}
- Top weak areas (algorithm-detected): {weak_list}

TASK:
1. Write "improvement_plan": 3 clear paragraphs with a 7-day revision strategy.
   - Address each weak area by name with specific Cambridge exam advice.
   - Reference command words, mark schemes, and examiner tips where relevant.
   - Keep language encouraging and actionable.

2. Write "summary": exactly 2 sentences.
   - Sentence 1: overall performance trajectory.
   - Sentence 2: the single most urgent area to address this week.

Return ONLY valid JSON (no markdown, no code fences):
{{"improvement_plan": "...", "summary": "..."}}"""

        raw = self.llm.generate_response(
            "Cambridge Academic Advisor", prompt, max_tokens=700, temperature=0.4
        )

        # Try strict JSON parse first
        try:
            parsed = json.loads(raw)
            return (
                parsed.get("improvement_plan", ""),
                parsed.get("summary", ""),
            )
        except (json.JSONDecodeError, ValueError):
            pass

        # Regex fallback for markdown-wrapped responses
        plan_match = re.search(r'"improvement_plan"\s*:\s*"((?:[^"\\]|\\.)*)"', raw, re.DOTALL)
        summ_match = re.search(r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)"', raw, re.DOTALL)

        plan = plan_match.group(1).replace("\\n", "\n") if plan_match else (
            f"Focus on your identified weak areas: {weak_list}. "
            "Review Cambridge mark schemes carefully and practise past papers regularly."
        )
        summary = summ_match.group(1) if summ_match else (
            "Your practice history shows room for improvement. "
            f"Prioritise {weak_areas[0].display_name if weak_areas else 'consistent revision'} this week."
        )
        return plan, summary

    # ── Readiness Score ───────────────────────────────────────────────────────

    @staticmethod
    def compute_readiness_score(scores: dict, total_interactions: int) -> float:
        """
        Estimate overall exam readiness as a percentage (20–95).
        - No data → 50 (neutral)
        - High weakness scores → lower readiness
        - More interactions → slightly higher confidence
        """
        if not scores or total_interactions < 2:
            return 50.0

        avg_weakness = sum(d["normalized_score"] for d in scores.values()) / len(scores)
        base = max(0.0, (1.0 - avg_weakness) * 100)

        # Reward volume of practice (log-scaled, caps at +10)
        practice_bonus = min(10.0, math.log1p(total_interactions) * 2)
        raw = base + practice_bonus

        # Clamp: never show 0% or 100% — always leave room for growth
        return round(max(20.0, min(95.0, raw)), 1)

    # ── Main Entry Point ──────────────────────────────────────────────────────

    def analyze(self, session_id: str) -> EnhancedWeaknessResponse:
        """Run full weakness analysis for a session and return a complete response."""
        interactions = get_session_interactions(session_id)

        if not interactions:
            return EnhancedWeaknessResponse(
                weak_areas=[],
                practice_questions=[],
                improvement_plan=(
                    "Start practising! Ask questions in any subject module to build "
                    "your personal performance profile. The more you interact, the more "
                    "accurate your weakness analysis becomes."
                ),
                summary=(
                    "No interactions recorded yet. "
                    "Begin studying to unlock your personalised AI analysis."
                ),
                overall_readiness_score=50.0,
                study_session_suggestion=(
                    "Pick any subject from the dashboard to get started."
                ),
                total_interactions=0,
            )

        scores = self.compute_weakness_scores(interactions)
        weak_areas = self.get_weak_areas(scores)
        practice_qs = self.get_practice_questions(weak_areas)
        plan, summary = self.generate_improvement_plan(weak_areas, interactions)
        readiness = self.compute_readiness_score(scores, len(interactions))

        suggestion = (
            f"Focus on {weak_areas[0].display_name} ({weak_areas[0].subject.title()}) today — "
            f"it's your highest-priority weak area."
            if weak_areas
            else "Great work! Keep practising to maintain your strong performance."
        )

        return EnhancedWeaknessResponse(
            weak_areas=weak_areas,
            practice_questions=practice_qs,
            improvement_plan=plan,
            summary=summary,
            overall_readiness_score=readiness,
            study_session_suggestion=suggestion,
            total_interactions=len(interactions),
        )

