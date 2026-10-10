"""API route routers package."""

from app.routes.health import router as health_router
from app.routes.extract import router as extract_router
from app.routes.embeddings import router as embeddings_router

__all__ = ["health_router", "extract_router", "embeddings_router"]
