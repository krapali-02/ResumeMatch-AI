"""Application configuration and environment variable validation."""

from functools import lru_cache
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the AI microservice."""

    APP_NAME: str = "ResumeMatch AI - Python AI Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False

    # Security: restrict CORS to explicit trusted origins
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
    ]

    # Input length safeguards (EC-09 / DoS mitigation)
    MAX_INPUT_TEXT_LENGTH: int = Field(
        default=150_000,
        description="Maximum characters accepted in a single text payload",
    )
    MAX_BATCH_SIZE: int = Field(
        default=64,
        description="Maximum texts accepted in a single batch embedding request",
    )

    # Embedding model settings
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSIONS: int = 384
    EMBEDDING_MODEL_CACHE_DIR: str = "models_cache"
    MOCK_EMBEDDINGS: bool = Field(
        default=False,
        description="Set to true for lightweight test runs without downloading live weights",
    )

    # Optional internal service authentication
    API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> List[str]:
        if isinstance(value, str):
            if value.startswith("[") and value.endswith("]"):
                import json

                try:
                    return json.loads(value)
                except Exception:
                    pass
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return [str(v) for v in value]
        return ["http://localhost:3000", "http://localhost:5000"]


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton instance of application settings."""
    return Settings()
