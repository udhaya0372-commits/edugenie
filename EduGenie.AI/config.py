from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "EduGenie"
    app_env: str = "development"
    cors_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    max_input_chars: int = Field(default=10000, ge=1)
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"
    local_explanation_model: str = "MBZUAI/LaMini-Flan-T5-783M"


@lru_cache
def get_settings() -> Settings:
    return Settings()
