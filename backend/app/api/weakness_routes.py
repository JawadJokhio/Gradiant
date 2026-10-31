"""
weakness_routes.py
GET  /analyze-weakness       — Full weakness analysis (fixes the live frontend bug)
POST /api/weakness/log       — Log a student interaction for tracking
"""
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.core.dependencies import get_data_repository, get_llm_service
from app.models.schemas import EnhancedWeaknessResponse
from app.repositories.data_repository import DataRepository
from app.services.llm_service import LLMService
from app.services.weakness_analyzer import (
    WeaknessAnalyzer,
    classify_topic,
    extract_marks_from_response,
)
from app.utils.session_store import log_interaction

router = APIRouter(tags=["Weakness Analysis"])


def get_weakness_analyzer(
    llm_service: LLMService = Depends(get_llm_service),
    data_repo: DataRepository = Depends(get_data_repository),
) -> WeaknessAnalyzer:
    return WeaknessAnalyzer(llm_service, data_repo)


# ─── GET /analyze-weakness ────────────────────────────────────────────────────

@router.get("/analyze-weakness", response_model=EnhancedWeaknessResponse)
async def analyze_weakness(
    x_session_id: Optional[str] = Header(default=None, alias="X-Session-ID"),
    analyzer: WeaknessAnalyzer = Depends(get_weakness_analyzer),
):
    """
    Returns a full weakness analysis for the student's current session.

    This endpoint is called by WeaknessAnalysis.jsx in the frontend.
    Requires the X-Session-ID header set by SessionTracker.jsx.
    Falls back to a default session if the header is absent.
    """
    session_id = x_session_id or "default_session"
    try:
        return analyzer.analyze(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


# ─── POST /api/weakness/log ───────────────────────────────────────────────────

class LogInteractionRequest(BaseModel):
    subject: str
    topic: str = "auto"          # "auto" triggers keyword-based classification
    question_text: str
    marks_available: int
    marks_obtained: Optional[int] = None
    mode: str = "text"           # "text" | "vision" | "mcq"
    llm_response: Optional[str] = None  # Raw LLM answer; used to extract examiner band


@router.post("/api/weakness/log")
async def log_student_interaction(
    request: LogInteractionRequest,
    x_session_id: Optional[str] = Header(default=None, alias="X-Session-ID"),
):
    """
    Log a single student interaction for weakness tracking.

    Called automatically by SessionTracker.jsx after every subject query.
    - If topic == "auto", backend classifies it from question_text keywords.
    - If marks_obtained is missing but llm_response is provided, marks are
      extracted from the [EXAMINER AUDIT: X/Y] line in the LLM response.
    """
    session_id = x_session_id or "default_session"

    # Auto-classify topic from question text if requested
    topic = request.topic
    if not topic or topic.strip().lower() == "auto":
        topic = classify_topic(request.question_text, request.subject)

    # Auto-extract marks from LLM response if not explicitly provided
    marks_obtained = request.marks_obtained
    if marks_obtained is None and request.llm_response:
        marks_obtained = extract_marks_from_response(
            request.llm_response, request.marks_available
        )

    try:
        interaction = log_interaction(
            session_id=session_id,
            subject=request.subject,
            topic=topic,
            question_text=request.question_text,
            marks_available=request.marks_available,
            marks_obtained=marks_obtained,
            mode=request.mode,
        )
        return {
            "logged": True,
            "interaction_id": interaction["id"],
            "topic_detected": topic,
            "marks_obtained": marks_obtained,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log interaction: {e}")

