"""Optional live integration test for Sentence Transformers all-MiniLM-L6-v2.

By default, unit tests use the deterministic mock to ensure instant,
offline-safe test runs without requiring multi-gigabyte downloads.
Set environment variable RUN_LIVE_MODEL_TESTS=1 to run this test.
"""

import math
import os
import pytest
from app.services.embedding_service import EmbeddingService


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_MODEL_TESTS") != "1",
    reason="Live SentenceTransformer model download test is skipped by default. Set RUN_LIVE_MODEL_TESTS=1 to enable.",
)
def test_live_sentence_transformer_inference():
    """Live verification of SentenceTransformer model download, caching, and inference."""
    # Force real model loading
    service = EmbeddingService(mock_mode=False)
    service.load_model()

    assert service.is_ready() is True

    test_sentences = [
        "Experienced software developer building microservices in Go and Python.",
        "Frontend React engineer designing accessible web components.",
    ]

    embeddings = service.encode(test_sentences)

    assert len(embeddings) == 2
    for vec in embeddings:
        assert len(vec) == 384
        norm = math.sqrt(sum(x * x for x in vec))
        assert pytest.approx(norm, abs=1e-5) == 1.0
