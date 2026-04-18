import os
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT_DIR = os.path.dirname(BACKEND_DIR)

class Settings(BaseSettings):
    """Application configuration and settings."""
    app_name: str = "Pakistan Geography Tutor - Personalized Examiner"
    
    # API Keys
    groq_api_key: str = Field(default="", validation_alias=AliasChoices("groq_api_key", "GROQ_API_KEY"))
    hf_api_key: str = Field(default="", validation_alias=AliasChoices("hf_api_key", "HF_API_KEY", "HUGGINGFACE_API_KEY"))
    openrouter_api_key: str = Field(default="", validation_alias=AliasChoices("openrouter_api_key", "OPENROUTER_API_KEY"))
    gemini_api_key: str = Field(default="", validation_alias=AliasChoices("gemini_api_key", "GEMINI_API_KEY", "GOOGLE_API_KEY"))

    # Database & Security
    mongo_uri: str = ""
    secret_key: str = "default_secret_key"

    # Paths
    # Calculated relative to app/core/config.py: 
    # config.py -> core -> app -> backend -> Gradiant (base_dir)
    base_dir: str = PROJECT_ROOT_DIR
    
    @property
    def hist_data_path(self) -> str:
        return os.path.join(self.base_dir, "data", "history_data.json")
    
    @property
    def geog_data_path(self) -> str:
        return os.path.join(self.base_dir, "data", "geography_data.json")

    @field_validator("groq_api_key", "hf_api_key", "openrouter_api_key", "gemini_api_key", mode="before")
    @classmethod
    def normalize_api_keys(cls, value):
        if not isinstance(value, str):
            return value
        return value.strip().strip('"').strip("'")

    model_config = SettingsConfigDict(
        env_file=(os.path.join(PROJECT_ROOT_DIR, ".env"), os.path.join(BACKEND_DIR, ".env")),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
