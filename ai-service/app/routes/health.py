"""Health and readiness probe router."""

from datetime import datetime, timezone
from fastapi import APIRouter, Response, status
from app.config import get_settings
from app.schemas.health import HealthResponse, ReadinessResponse
from app.services.embedding_service import EmbeddingService
from app.services.skill_ontology import get_canonical_ontology

router = APIRouter(tags=["Health & Monitoring"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness Probe",
    description="Confirms that the FastAPI process is alive and responsive.",
)
def get_liveness() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness Probe",
    description="Reports whether AI models, skill dictionaries, and encoders are operational.",
)
def get_readiness(response: Response) -> ReadinessResponse:
    settings = get_settings()
    embedding_service = EmbeddingService.get_instance()

    ontology_ok = len(get_canonical_ontology()) > 0
    model_ready = embedding_service.is_ready()

    is_overall_ready = ontology_ok and (model_ready or settings.MOCK_EMBEDDINGS)

    if not is_overall_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status="ready" if is_overall_ready else "not_ready",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        model_name=settings.EMBEDDING_MODEL_NAME,
        model_loaded=model_ready,
        skill_ontology_ready=ontology_ok,
        mock_mode=embedding_service.mock_mode,
        details={
            "ontology_skills_count": len(get_canonical_ontology()),
            "embedding_dimensions": settings.EMBEDDING_DIMENSIONS,
            "environment": settings.ENVIRONMENT,
        },
    )
