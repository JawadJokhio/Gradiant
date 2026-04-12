from pydantic import BaseModel
from typing import List, Optional

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
