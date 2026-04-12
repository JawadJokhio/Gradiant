import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration and settings."""
    app_name: str = "Pakistan Geography Tutor - Personalized Examiner"
    
    # API Keys
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    hf_api_key: str = os.getenv("HF_API_KEY", "")

    # Paths
    base_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    hist_data_path: str = os.path.join(base_dir, "data", "history_data.json")
    geog_data_path: str = os.path.join(base_dir, "data", "geography_data.json")

    class Config:
        env_file = ".env"

settings = Settings()
