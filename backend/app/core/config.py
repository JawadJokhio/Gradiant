import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration and settings."""
    app_name: str = "Pakistan Geography Tutor - Personalized Examiner"
    
    # API Keys
    groq_api_key: str = ""
    hf_api_key: str = ""

    # Database & Security
    mongo_uri: str = ""
    secret_key: str = "default_secret_key"

    # Paths
    # Calculated relative to app/core/config.py: 
    # config.py -> core -> app -> backend -> Gradiant (base_dir)
    base_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    @property
    def hist_data_path(self) -> str:
        return os.path.join(self.base_dir, "data", "history_data.json")
    
    @property
    def geog_data_path(self) -> str:
        return os.path.join(self.base_dir, "data", "geography_data.json")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
