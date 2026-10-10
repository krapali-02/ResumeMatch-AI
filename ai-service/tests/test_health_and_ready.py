"""Unit and integration tests for health and readiness endpoints."""

from fastapi.testclient import TestClient
from app.services.embedding_service import EmbeddingService


def test_health_liveness_endpoint(client: TestClient):
    """Verify /health liveness probe confirms process is alive with 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ResumeMatch AI" in data["service"]
    assert "1.0.0" in data["version"]
    assert "timestamp" in data


def test_prefixed_health_liveness_endpoint(client: TestClient):
    """Verify /api/v1/health also responds with 200 OK."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readiness_probe_when_ready(client: TestClient):
    """Verify /ready probe reports operational status when components are initialized."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["skill_ontology_ready"] is True
    assert data["model_name"] == "all-MiniLM-L6-v2"


def test_readiness_probe_when_not_ready(client: TestClient, monkeypatch):
    """Verify /ready probe accurately reports 503 when required component is unready."""
    # Simulate unready embedding service without mock mode
    service = EmbeddingService.get_instance()
    monkeypatch.setattr(service, "mock_mode", False)
    monkeypatch.setattr(service, "_is_loaded", False)
    monkeypatch.setattr(service, "_model", None)

    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "MOCK_EMBEDDINGS", False)

    response = client.get("/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "not_ready"
    assert data["model_loaded"] is False
