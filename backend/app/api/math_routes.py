"""
Math API Routes
POST /api/math/solve   — solve a math question step-by-step
GET  /api/math/concepts        — list all concept keys
GET  /api/math/concepts/{key}  — get a concept by key
"""

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field, field_validator

from app.services.math_service import solve_math_question
from app.services.math_concepts import get_concept, list_all_concepts

router = APIRouter(prefix="/api/math", tags=["Math"])


# ── Request / Response Models ─────────────────────────────────────────────────

class MathSolveRequest(BaseModel):
    question: str = Field(..., min_length=3, description="The math question text")
    question_number: int = Field(1, ge=1, le=100, description="Question number (optional)")
    marks: int = Field(..., ge=1, le=20, description="Number of marks for this question")

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Question cannot be empty.")
        return v


class MathStep(BaseModel):
    step_number: int
    description: str
    expression: str
    concept_key: str | None


class MathSolveResponse(BaseModel):
    question_number: int
    marks: int
    steps: list[MathStep]
    final_answer: str
    mark_commentary: str
    raw_question: str


class ConceptResponse(BaseModel):
    key: str
    title: str
    explanation: str
    example: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/solve", response_model=MathSolveResponse)
async def solve(request: MathSolveRequest):
    """
    Solve an O-Level math question and return structured step-by-step solution.
    Marks are mandatory and control the depth of the solution.
    """
    try:
        result = solve_math_question(
            question=request.question,
            question_number=request.question_number,
            marks=request.marks,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Math solver error: {str(e)}")


@router.get("/concepts", response_model=list[str])
async def get_all_concepts():
    """Return a sorted list of all concept keys."""
    return list_all_concepts()


@router.get("/concepts/{key}", response_model=ConceptResponse)
async def get_concept_by_key(key: str):
    """Return a concept explanation by its key."""
    data = get_concept(key)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Concept '{key}' not found. Call /api/math/concepts for a full list.",
        )
    return ConceptResponse(
        key=key.lower(),
        title=data["title"],
        explanation=data["explanation"],
        example=data["example"],
    )
