from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.core.dependencies import get_paper_service
from app.services.paper_service import PaperService

router = APIRouter(tags=["Papers"])

@router.get("/papers/{subject}/years", response_model=List[str])
async def get_paper_years(
    subject: str,
    paper_service: PaperService = Depends(get_paper_service)
):
    return paper_service.get_paper_years(subject)

@router.get("/papers/{subject}/{year}", response_model=List[str])
async def get_paper_sessions(
    subject: str, 
    year: str,
    paper_service: PaperService = Depends(get_paper_service)
):
    return paper_service.get_paper_sessions(subject, year)

@router.get("/papers/{subject}/{year}/{session}", response_model=Dict[str, Any])
async def get_paper_content(
    subject: str, 
    year: str, 
    session: str,
    paper_service: PaperService = Depends(get_paper_service)
):
    return paper_service.get_paper_content(subject, year, session)
