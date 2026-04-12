from fastapi import Depends
from app.repositories.data_repository import DataRepository
from app.services.llm_service import LLMService
from app.services.history_context_service import HistoryContextService
from app.services.geography_service import GeographyService
from app.services.paper_service import PaperService
from app.services.geography_image_service import GeographyImageAnalysisService

# Singletons
_data_repository = DataRepository()
_llm_service = LLMService()

def get_data_repository() -> DataRepository:
    return _data_repository

def get_llm_service() -> LLMService:
    return _llm_service

def get_history_context_service(data_repository: DataRepository = Depends(get_data_repository)) -> HistoryContextService:
    return HistoryContextService(data_repository)

def get_geography_service(data_repository: DataRepository = Depends(get_data_repository)) -> GeographyService:
    return GeographyService(data_repository)

def get_paper_service(data_repository: DataRepository = Depends(get_data_repository)) -> PaperService:
    return PaperService(data_repository)

def get_geography_image_analysis_service(llm_service: LLMService = Depends(get_llm_service)) -> GeographyImageAnalysisService:
    return GeographyImageAnalysisService(llm_service)
