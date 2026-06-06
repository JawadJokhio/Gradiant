from app.core.config import settings
from app.utils.helpers import load_json
from typing import Dict, Any

class DataRepository:
    """
    Singleton data repository to cache JSON datasets in-memory and provide access.
    """
    _instance = None
    _history_data: Dict[str, Any] = {}
    _geography_data: Dict[str, Any] = {}
    _history_sources_data: Dict[str, Any] = {}
    _math_data: Dict[str, Any] = {}
    _economics_data: Dict[str, Any] = {}
    _economics_past_papers_data: Dict[str, Any] = {}
    _loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataRepository, cls).__new__(cls)
        return cls._instance

    def _ensure_loaded(self):
        if not self._loaded:
            self._history_data = load_json(settings.hist_data_path)
            self._geography_data = load_json(settings.geog_data_path)
            self._history_sources_data = load_json(settings.history_sources_data_path)
            self._math_data = load_json("app/data/math_dataset.json")
            self._economics_data = load_json(settings.econ_data_path)
            self._economics_past_papers_data = load_json(settings.econ_past_papers_path)
            self._loaded = True

    def get_history_data(self) -> Dict[str, Any]:
        self._ensure_loaded()
        return self._history_data

    def get_geography_data(self) -> Dict[str, Any]:
        self._ensure_loaded()
        return self._geography_data

    def get_history_sources_data(self) -> Dict[str, Any]:
        self._ensure_loaded()
        return self._history_sources_data

    def get_math_data(self) -> Dict[str, Any]:
        self._ensure_loaded()
        return self._math_data

    def get_economics_data(self) -> Dict[str, Any]:
        self._ensure_loaded()
        return self._economics_data

    def get_economics_past_papers_data(self) -> Dict[str, Any]:
        self._ensure_loaded()
        return self._economics_past_papers_data
