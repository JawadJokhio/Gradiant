import sys
from app.repositories.data_repository import DataRepository

class PaperService:
    def __init__(self, data_repository: DataRepository):
        self.data_repository = data_repository

    def get_paper_years(self, subject: str) -> list[str]:
        data = self._get_subject_data(subject)
        past_papers = data.get("past_papers", {})
        return sorted(list(past_papers.keys()), reverse=True)

    def get_paper_sessions(self, subject: str, year: str) -> list[str]:
        data = self._get_subject_data(subject)
        year_data = data.get("past_papers", {}).get(year, {})
        return list(year_data.keys())

    def get_paper_content(self, subject: str, year: str, session: str) -> dict:
        data = self._get_subject_data(subject)
        session_data = data.get("past_papers", {}).get(year, {}).get(session, {})
        return session_data

    def _get_subject_data(self, subject: str) -> dict:
        if subject.lower() == "history":
            return self.data_repository.get_history_data()
        else:
            return self.data_repository.get_geography_data()
