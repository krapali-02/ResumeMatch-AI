"""Health and readiness endpoint response schemas."""

from typing import Any, Dict
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness probe response confirming process health."""

    status: str = Field(default="ok", description="Service liveness state")
    service: str = Field(description="Name of the service")
    version: str = Field(description="Service semantic version")
    timestamp: str = Field(description="ISO-8601 UTC timestamp")


class ReadinessResponse(BaseModel):
    """Readiness probe response detailing component operational statuses."""

    status: str = Field(description="Readiness state: 'ready' or 'not_ready'")
    service: str = Field(description="Name of the service")
    version: str = Field(description="Service semantic version")
    model_name: str = Field(description="Configured embedding model")
    model_loaded: bool = Field(description="Whether the embedding model is loaded")
    skill_ontology_ready: bool = Field(description="Whether skill ontology is compiled")
    mock_mode: bool = Field(description="Whether mock embedding mode is active")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed sub-check results")
