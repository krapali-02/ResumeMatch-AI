"""ResumeMatch AI — Python AI Service Application Entry Point."""

from contextlib import asynccontextmanager
import logging
import sys
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routes.embeddings import router as embeddings_router
from app.routes.extract import router as extract_router
from app.routes.health import router as health_router
from app.services.embedding_service import EmbeddingService

# Configure structured application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("resumematch.ai")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for resource initialization and cleanup."""
    settings = get_settings()
    logger.info("Initializing %s v%s...", settings.APP_NAME, settings.APP_VERSION)

    # Initialize embedding service in background or eager load
    try:
        embedding_service = EmbeddingService.get_instance()
        if not settings.MOCK_EMBEDDINGS:
            # Load model once at startup to warm up process
            embedding_service.load_model()
            logger.info("Embedding service model pre-loaded successfully.")
        else:
            logger.info("Embedding service running in deterministic mock mode.")
    except Exception as exc:
        logger.warning(
            "Warmup model loading deferred or failed (%s). Service will attempt lazy initialization.",
            exc,
        )

    yield

    logger.info("Shutting down %s...", settings.APP_NAME)


def create_application() -> FastAPI:
    """FastAPI application factory with security middleware and error interceptors."""
    settings = get_settings()

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Candidate Information Extraction and Semantic Dense Embeddings Microservice",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    # Security: Restrict CORS to trusted origins only
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    )

    # Security: Content-Length payload limiter (Reject payloads > 10MB)
    @application.middleware("http")
    async def limit_upload_size(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > 10 * 1024 * 1024:  # 10 MB limit
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"error": "Payload exceeds maximum allowed size of 10MB."},
                    )
            except ValueError:
                pass
        return await call_next(request)

    # Error handling: suppress stack traces and return clean JSON
    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "details": [
                    {
                        "loc": err.get("loc"),
                        "msg": err.get("msg"),
                        "type": err.get("type"),
                    }
                    for err in exc.errors()
                ],
            },
        )

    @application.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Log error internally without exposing raw traceback to client
        logger.error("Unhandled server exception on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error occurred."},
        )

    # Include route modules
    application.include_router(health_router)
    # Also register /api/v1/health and /api/v1/ready for flexible gateway routing
    application.include_router(health_router, prefix="/api/v1")
    application.include_router(extract_router)
    application.include_router(embeddings_router)

    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn

    config = get_settings()
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
    )
