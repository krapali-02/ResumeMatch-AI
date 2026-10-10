"""Unit tests for embedding generation, dimensionality, normalization, and failure modes."""

import math
import numpy as np
import pytest
from app.services.embedding_service import EmbeddingService, EmbeddingServiceError


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    a = np.array(v1, dtype=np.float32)
    b = np.array(v2, dtype=np.float32)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def test_embedding_dimensions_and_normalization():
    """Verify generated vector has exactly 384 dimensions and unit length (FR-MATCH-02, EC-26)."""
    service = EmbeddingService(mock_mode=True)
    embeddings = service.encode("Senior Python and React Developer")

    assert len(embeddings) == 1
    vector = embeddings[0]

    # Verify exactly 384 dimensions
    assert len(vector) == 384

    # Verify L2 unit norm (||v|| = 1.0)
    norm = math.sqrt(sum(x * x for x in vector))
    assert pytest.approx(norm, abs=1e-5) == 1.0


def test_batch_embedding_generation():
    """Verify batch inputs generate corresponding list of 384-dimensional vectors."""
    service = EmbeddingService(mock_mode=True)
    texts = [
        "Kubernetes orchestration specialist",
        "Frontend React and Vue engineer",
        "PostgreSQL database administrator",
    ]
    embeddings = service.encode(texts)

    assert len(embeddings) == 3
    for vec in embeddings:
        assert len(vec) == 384
        norm = math.sqrt(sum(x * x for x in vec))
        assert pytest.approx(norm, abs=1e-5) == 1.0


def test_cosine_similarity_prerequisites():
    """Verify identical texts produce identical vectors with cosine similarity of 1.0."""
    service = EmbeddingService(mock_mode=True)
    text = "Machine Learning Engineer with PyTorch experience"

    emb1 = service.encode(text)[0]
    emb2 = service.encode(text)[0]

    # Exact deterministic equivalence
    assert emb1 == emb2

    similarity = cosine_similarity(emb1, emb2)
    assert pytest.approx(similarity, abs=1e-5) == 1.0


def test_different_texts_produce_bounded_similarity():
    """Verify distinct texts produce bounded cosine similarities in [-1.0, 1.0]."""
    service = EmbeddingService(mock_mode=True)
    emb1 = service.encode("Cloud infrastructure engineer")[0]
    emb2 = service.encode("Executive pastry chef")[0]

    similarity = cosine_similarity(emb1, emb2)
    assert -1.0 <= similarity <= 1.0


def test_empty_string_rejection():
    """Verify empty or whitespace-only inputs raise ValueError."""
    service = EmbeddingService(mock_mode=True)

    with pytest.raises(ValueError, match="cannot be empty"):
        service.encode("")

    with pytest.raises(ValueError, match="cannot be empty"):
        service.encode("   \t\n   ")

    with pytest.raises(ValueError, match="cannot be empty"):
        service.encode([])

    with pytest.raises(ValueError, match="cannot be empty"):
        service.encode(["Valid text", "   "])


def test_excessive_length_rejection(monkeypatch):
    """Verify inputs exceeding MAX_INPUT_TEXT_LENGTH raise ValueError (EC-09)."""
    service = EmbeddingService(mock_mode=True)
    monkeypatch.setattr(service.settings, "MAX_INPUT_TEXT_LENGTH", 100)

    oversized_text = "A" * 150
    with pytest.raises(ValueError, match="exceeds maximum allowed length"):
        service.encode(oversized_text)


def test_model_loading_failure_handling(monkeypatch):
    """Verify model initialization errors raise EmbeddingServiceError with 503 code."""
    service = EmbeddingService(mock_mode=False)

    def mock_broken_st(*args, **kwargs):
        raise RuntimeError("Failed to load model weights: File corrupted")

    # Patch import or sentence_transformers
    import sentence_transformers
    monkeypatch.setattr(sentence_transformers, "SentenceTransformer", mock_broken_st)

    with pytest.raises(EmbeddingServiceError) as exc_info:
        service.load_model()

    assert exc_info.value.status_code == 503
    assert "Model initialization failed" in exc_info.value.message


def test_model_inference_failure_handling(monkeypatch):
    """Verify inference exceptions raise EmbeddingServiceError with 500 code."""
    service = EmbeddingService(mock_mode=False)

    class MockFailingModel:
        def encode(self, *args, **kwargs):
            raise RuntimeError("CUDA device out of memory")

    service._model = MockFailingModel()
    service._is_loaded = True

    with pytest.raises(EmbeddingServiceError) as exc_info:
        service.encode("Valid text input")

    assert exc_info.value.status_code == 500
    assert "Embedding inference failed" in exc_info.value.message
