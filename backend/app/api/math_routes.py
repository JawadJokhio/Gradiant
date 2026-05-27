"""
Math API Routes
POST /api/math/solve   — solve a math question step-by-step
POST /api/math/analyze-image — solve a math question from an image
GET  /api/math/concepts        — list all concept keys
GET  /api/math/concepts/{key}  — get a concept by key
"""

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field, field_validator

from app.services.math_service import solve_math_question, solve_math_image_question
from app.services.math_concepts import get_concept, list_all_concepts
from app.utils.helpers import extract_base64_from_file

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
    visual_data: str | None = None


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


@router.post("/analyze-image", response_model=MathSolveResponse)
async def analyze_image(
    image: UploadFile = File(...),
    query: str = Form(""),
    marks: int = Form(4)
):
    """
    Solves a math question from an uploaded image.
    Includes subject relevance validation.
    """
    try:
        content = await image.read()
        base64_img = extract_base64_from_file(content)
        
        result = solve_math_image_question(
            image_base64=base64_img,
            query=query,
            marks=marks
        )
        
        if "error" in result:
            # If it's a relevance error, we return it in a way the frontend can handle or raise 400
            # Thinking: User asked for a "prompt" showing the message.
            # We can return it inside the response so the frontend shows it nicely.
            # But the schema requires steps. We can use a single step to show the error.
            return MathSolveResponse(
                question_number=1,
                marks=marks,
                steps=[{
                    "step_number": 1,
                    "description": "Validation Error",
                    "expression": result["message"],
                    "concept_key": None
                }],
                final_answer="Subject Irrelevant",
                mark_commentary=result.get("relevance_reason", "Not Math"),
                raw_question="Image Upload"
            )
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Math image solver error: {str(e)}")


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
