"""Semantic embedding generation API endpoint."""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.config import get_settings
from app.schemas.embedding import EmbeddingRequest, EmbeddingResponse
from app.services.embedding_service import EmbeddingService, EmbeddingServiceError

logger = logging.getLogger("resumematch.ai.embeddings")
router = APIRouter(prefix="/api/v1", tags=["Embeddings"])


@router.post(
    "/embeddings",
    response_model=EmbeddingResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Semantic Dense Embeddings",
    description="Encodes text inputs into 384-dimensional dense vectors normalized for cosine similarity.",
)
def generate_embeddings(payload: EmbeddingRequest) -> EmbeddingResponse:
    settings = get_settings()

    # Collect input strings
    if payload.texts is not None and len(payload.texts) > 0:
        inputs: List[str] = payload.texts
    elif payload.text is not None and bool(payload.text.strip()):
        inputs = [payload.text.strip()]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload must supply either 'text' or 'texts'.",
        )

    # Batch size limit guard
    if len(inputs) > settings.MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch size ({len(inputs)}) exceeds maximum allowed batch of {settings.MAX_BATCH_SIZE}.",
        )

    embedding_service = EmbeddingService.get_instance()

    try:
        embeddings = embedding_service.encode(inputs)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except EmbeddingServiceError as emb_err:
        logger.error("Embedding generation service error: %s", emb_err.message)
        raise HTTPException(
            status_code=emb_err.status_code,
            detail=emb_err.message,
        ) from emb_err
    except Exception as exc:
        logger.error("Unexpected embedding failure: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during embedding inference.",
        ) from exc

    return EmbeddingResponse(
        model=settings.EMBEDDING_MODEL_NAME,
        dimensions=settings.EMBEDDING_DIMENSIONS,
        embeddings=embeddings,
        normalized=True,
        count=len(embeddings),
    )
