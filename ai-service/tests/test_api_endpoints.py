"""API endpoint integration tests covering extraction, embeddings, validation, and security."""

from fastapi.testclient import TestClient


def test_extract_endpoint_success(client: TestClient, sample_resume_text):
    """Verify POST /api/v1/extract returns structured profile with evidence."""
    payload = {
        "text": sample_resume_text,
        "candidate_id": "cand_12345",
    }
    response = client.post("/api/v1/extract", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["candidate_id"] == "cand_12345"
    assert data["character_count"] > 100
    assert data["contains_prompt_injection_attempt"] is False

    # Verify extracted primary skills and tools
    skill_names = [s["canonical_name"] for s in data["skills"]]
    tool_names = [s["canonical_name"] for s in data["technical_tools"]]
    all_names = skill_names + tool_names

    assert "TypeScript" in all_names
    assert "React" in all_names
    assert "PostgreSQL" in all_names
    assert "Kubernetes" in all_names
    assert "Docker" in all_names
    assert "FastAPI" in all_names

    # Check evidence preservation
    k8s_skill = next((s for s in data["technical_tools"] if s["canonical_name"] == "Kubernetes"), None)
    assert k8s_skill is not None
    assert k8s_skill["matched_text"].lower() in ("k8s", "kubernetes")
    assert "AWS" in k8s_skill["evidence_snippet"] or "Kubernetes" in k8s_skill["evidence_snippet"]

    # Verify education
    assert data["education_status"] == "identified"
    assert len(data["education"]) >= 1
    assert data["education"][0]["degree"] == "Bachelor of Science"

    # Verify experience tenure
    assert data["experience_summary"]["status"] == "identified"
    assert data["experience_summary"]["explicit_years_of_experience"] == 6.0

    # Verify roles
    assert data["roles_status"] == "identified"
    assert len(data["roles"]) >= 1


def test_extract_endpoint_empty_text_rejection(client: TestClient):
    """Verify empty or whitespace-only text is rejected with 422 Unprocessable Entity."""
    response = client.post("/api/v1/extract", json={"text": "   "})
    assert response.status_code == 422
    assert "error" in response.json()


def test_extract_endpoint_missing_text_rejection(client: TestClient):
    """Verify request missing 'text' field is rejected with 422."""
    response = client.post("/api/v1/extract", json={"candidate_id": "cand_1"})
    assert response.status_code == 422


def test_extract_endpoint_oversized_payload_rejection(client: TestClient, monkeypatch):
    """Verify input text exceeding length limit is rejected with 400 (EC-09)."""
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "MAX_INPUT_TEXT_LENGTH", 200)

    payload = {"text": "A" * 250}
    response = client.post("/api/v1/extract", json=payload)
    assert response.status_code == 400
    assert "exceeds maximum allowed length" in response.json()["error"]


def test_extract_endpoint_adversarial_prompt_injection(client: TestClient, adversarial_resume_text):
    """Verify prompt injection attacks are treated as passive data without compromising the system (EC-15)."""
    payload = {
        "text": adversarial_resume_text,
        "candidate_id": "cand_hacker_99",
    }
    response = client.post("/api/v1/extract", json=payload)
    assert response.status_code == 200

    data = response.json()
    # Injected instructions must NOT alter output structure or crash service
    assert data["contains_prompt_injection_attempt"] is True
    assert any("Adversarial instruction pattern detected" in note for note in data["extraction_notes"])

    # Legitimate candidate skills must still be cleanly extracted
    extracted_skills = [s["canonical_name"] for s in data["skills"]]
    assert "Python" in extracted_skills
    assert "Django" in extracted_skills


def test_extract_endpoint_unknown_information_state(client: TestClient):
    """Verify missing optional attributes yield 'unknown' rather than failure (EC-08)."""
    sparse_text = "Experienced freelancer working with Python and PostgreSQL."
    response = client.post("/api/v1/extract", json={"text": sparse_text})
    assert response.status_code == 200

    data = response.json()
    assert data["education_status"] == "unknown"
    assert data["education"] == []
    assert data["experience_summary"]["status"] == "unknown"
    assert data["experience_summary"]["explicit_years_of_experience"] is None


def test_embeddings_endpoint_single_text(client: TestClient):
    """Verify POST /api/v1/embeddings generates 384-dimensional vector for single text."""
    payload = {"text": "Senior Cloud DevOps Engineer with Terraform and AWS"}
    response = client.post("/api/v1/embeddings", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["dimensions"] == 384
    assert data["model"] == "all-MiniLM-L6-v2"
    assert data["normalized"] is True
    assert data["count"] == 1
    assert len(data["embeddings"]) == 1
    assert len(data["embeddings"][0]) == 384


def test_embeddings_endpoint_batch_texts(client: TestClient):
    """Verify POST /api/v1/embeddings generates vectors for multiple texts."""
    payload = {
        "texts": [
            "Full Stack Web Developer",
            "Machine Learning Scientist",
            "Database Administrator",
        ]
    }
    response = client.post("/api/v1/embeddings", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 3
    assert len(data["embeddings"]) == 3
    for vec in data["embeddings"]:
        assert len(vec) == 384


def test_embeddings_endpoint_empty_inputs_rejection(client: TestClient):
    """Verify missing or empty inputs are rejected."""
    # Neither text nor texts
    response = client.post("/api/v1/embeddings", json={})
    assert response.status_code == 422

    # Empty string text
    response2 = client.post("/api/v1/embeddings", json={"text": "   "})
    assert response2.status_code == 422

    # Empty list texts
    response3 = client.post("/api/v1/embeddings", json={"texts": []})
    assert response3.status_code == 422


def test_embeddings_endpoint_batch_limit_rejection(client: TestClient, monkeypatch):
    """Verify exceeding MAX_BATCH_SIZE is rejected with 400 Bad Request."""
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "MAX_BATCH_SIZE", 3)

    payload = {"texts": ["Text 1", "Text 2", "Text 3", "Text 4"]}
    response = client.post("/api/v1/embeddings", json=payload)
    assert response.status_code == 400
    assert "exceeds maximum allowed batch" in response.json()["error"]


def test_stack_trace_suppression_on_internal_error(client: TestClient, monkeypatch):
    """Verify unhandled exceptions return clean JSON error without exposing tracebacks."""
    from app.services.embedding_service import EmbeddingService

    def mock_broken_encode(*args, **kwargs):
        raise RuntimeError("Secret internal database connection string: db://user:pass@host")

    service = EmbeddingService.get_instance()
    monkeypatch.setattr(service, "encode", mock_broken_encode)

    response = client.post("/api/v1/embeddings", json={"text": "Hello world"})
    assert response.status_code == 500
    data = response.json()
    # Confirm stack trace and internal secrets are suppressed
    assert "error" in data
    assert "Secret internal database connection string" not in response.text
    assert "Traceback" not in response.text
