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
    _loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataRepository, cls).__new__(cls)
        return cls._instance

    def _ensure_loaded(self):
        if not self._loaded:
            self._history_data = load_json(settings.hist_data_path)
            self._geography_data = load_json(settings.geog_data_path)
            self._loaded = True

    def get_history_data(self) -> Dict[str, Any]:
        self._ensure_loaded()
        return self._history_data

    def get_geography_data(self) -> Dict[str, Any]:
        self._ensure_loaded()
        return self._geography_data
