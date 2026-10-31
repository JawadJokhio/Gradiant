from pydantic import BaseModel
from typing import List, Optional

# ─── Existing Schemas ─────────────────────────────────────────────────────────

class WeaknessAnalysisResponse(BaseModel):
    weak_areas: List[str]
    improvement_plan: str
    summary: str

class PaperSession(BaseModel):
    session_name: str
    papers: List[str]

class YearlyPapers(BaseModel):
    year: str
    sessions: List[PaperSession]

class AIAnswerResponse(BaseModel):
    answer: str
    marks: int

class MapAnalysisResponse(BaseModel):
    features: list
    explanation: str
    query: str

# ─── OCR Schemas ─────────────────────────────────────────────────────────────

class TextBlock(BaseModel):
    text: str
    confidence: float
    bbox: Optional[list] = None   # Bounding box [x1, y1, x2, y2]

class OCRResult(BaseModel):
    raw_text: str
    confidence: float             # Average confidence across all blocks
    blocks: List[TextBlock]
    language_detected: str        # "en" | "ur" | "mixed"
    processing_time_ms: float

# ─── Weakness Tracking Schemas ────────────────────────────────────────────────

class WeakArea(BaseModel):
    topic: str
    subject: str
    weakness_score: float         # 0.0 – 1.0
    attempts: int
    last_attempted: Optional[str] = None
    display_name: str

class PracticeQuestion(BaseModel):
    question_id: str
    subject: str
    topic: str
    question_text: str
    marks: int
    year: Optional[str] = None
    difficulty: str               # "easy" | "medium" | "hard"
    why_recommended: str

class EnhancedWeaknessResponse(BaseModel):
    weak_areas: List[WeakArea]
    practice_questions: List[PracticeQuestion]
    improvement_plan: str
    summary: str
    overall_readiness_score: float
    study_session_suggestion: str
    total_interactions: int
