"""Dense vector embedding service using Sentence Transformers and all-MiniLM-L6-v2."""

import hashlib
import logging
import os
import threading
from typing import List, Optional, Union
import numpy as np

from app.config import get_settings

logger = logging.getLogger("resumematch.ai.embeddings")


class EmbeddingServiceError(Exception):
    """Domain exception raised when embedding generation or model loading fails."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class EmbeddingService:
    """Service responsible for loading sentence transformer models and computing normalized dense vectors."""

    _instance: Optional["EmbeddingService"] = None
    _lock = threading.Lock()

    def __init__(self, mock_mode: Optional[bool] = None):
        self.settings = get_settings()
        self.model_name = self.settings.EMBEDDING_MODEL_NAME
        self.expected_dimensions = self.settings.EMBEDDING_DIMENSIONS
        self.cache_dir = os.path.abspath(self.settings.EMBEDDING_MODEL_CACHE_DIR)
        self.mock_mode = (
            mock_mode if mock_mode is not None else self.settings.MOCK_EMBEDDINGS
        )
        self._model = None
        self._is_loaded = False
        self._load_lock = threading.Lock()

        # Ensure model cache folder exists outside tracked source files
        os.makedirs(self.cache_dir, exist_ok=True)

    @classmethod
    def get_instance(cls, mock_mode: Optional[bool] = None) -> "EmbeddingService":
        """Thread-safe singleton accessor."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(mock_mode=mock_mode)
            elif mock_mode is not None and cls._instance.mock_mode != mock_mode:
                cls._instance.mock_mode = mock_mode
            return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (useful for unit tests)."""
        with cls._lock:
            cls._instance = None

    def is_ready(self) -> bool:
        """Check whether embedding service is loaded and ready to serve."""
        if self.mock_mode:
            return True
        return self._is_loaded and self._model is not None

    def load_model(self) -> None:
        """Load Sentence Transformers model into memory if not in mock mode."""
        if self.mock_mode:
            self._is_loaded = True
            logger.info("EmbeddingService operating in deterministic MOCK mode.")
            return

        with self._load_lock:
            if self._is_loaded and self._model is not None:
                return

            try:
                logger.info(
                    "Loading embedding model '%s' from cache '%s'...",
                    self.model_name,
                    self.cache_dir,
                )
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(
                    self.model_name,
                    cache_folder=self.cache_dir,
                )
                self._is_loaded = True
                logger.info("Successfully loaded embedding model '%s'.", self.model_name)
            except Exception as exc:
                self._is_loaded = False
                self._model = None
                logger.error(
                    "Failed to initialize embedding model '%s': %s",
                    self.model_name,
                    exc,
                )
                raise EmbeddingServiceError(
                    f"Model initialization failed: {type(exc).__name__}",
                    status_code=503,
                ) from exc

    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate a deterministic 384-dimensional unit-normalized vector for testing (EC-26).

        Guarantees:
            - Exactly 384 dimensions.
            - L2 unit norm (||vec|| == 1.0).
            - Identical text always maps to identical vector.
            - Cosine similarity between identical texts is 1.0.
            - Bounded cosine similarity in [-1.0, 1.0].
            - Zero external network dependencies.
        """
        # Hash text to seed deterministic pseudorandom vector
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)
        rng = np.random.RandomState(seed)
        raw_vec = rng.randn(self.expected_dimensions).astype(np.float32)

        # Apply strict L2 unit normalization
        norm = np.linalg.norm(raw_vec)
        if norm > 0:
            norm_vec = raw_vec / norm
        else:
            norm_vec = raw_vec

        assert (
            len(norm_vec) == self.expected_dimensions
        ), f"Expected {self.expected_dimensions} dimensions, got {len(norm_vec)}"
        return norm_vec.tolist()

    def _normalize_vector(self, vec: np.ndarray) -> np.ndarray:
        """Strict L2 unit normalization for cosine similarity."""
        norm = np.linalg.norm(vec)
        if norm > 1e-12:
            return vec / norm
        return vec

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
    ) -> List[List[float]]:
        """Encode input text or batch of texts into 384-dimensional dense vectors.

        Args:
            texts: Single string or list of strings
            batch_size: Batch size for model inference

        Returns:
            List of 384-dimensional L2-normalized float vectors

        Raises:
            ValueError: If input is empty or invalid
            EmbeddingServiceError: If model inference fails
        """
        if isinstance(texts, str):
            input_list = [texts]
        elif isinstance(texts, list):
            input_list = texts
        else:
            raise ValueError("Input must be a string or a list of strings.")

        if not input_list:
            raise ValueError("Input text list cannot be empty.")

        # Validate each string
        cleaned_inputs: List[str] = []
        for idx, item in enumerate(input_list):
            if not isinstance(item, str) or not item.strip():
                raise ValueError(
                    f"Text at index {idx} cannot be empty or solely whitespace."
                )
            # Guard against excessive input length (EC-09)
            if len(item) > self.settings.MAX_INPUT_TEXT_LENGTH:
                raise ValueError(
                    f"Text at index {idx} exceeds maximum allowed length of {self.settings.MAX_INPUT_TEXT_LENGTH} characters."
                )
            cleaned_inputs.append(item.strip())

        # If mock mode is active, return deterministic vectors
        if self.mock_mode:
            return [self._generate_mock_embedding(t) for t in cleaned_inputs]

        # Ensure live model is loaded
        if not self._is_loaded or self._model is None:
            self.load_model()

        try:
            # Generate embeddings via SentenceTransformer with internal L2 normalization
            raw_embeddings = self._model.encode(
                cleaned_inputs,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

            # Verification of output dimensions and normalization (EC-26)
            normalized_results: List[List[float]] = []
            for vec in raw_embeddings:
                if len(vec) != self.expected_dimensions:
                    raise EmbeddingServiceError(
                        f"Unexpected vector dimension: got {len(vec)}, expected {self.expected_dimensions}",
                        status_code=500,
                    )
                # Ensure float precision and exact unit norm
                unit_vec = self._normalize_vector(vec)
                normalized_results.append([float(x) for x in unit_vec])

            return normalized_results

        except EmbeddingServiceError:
            raise
        except Exception as exc:
            logger.error("Embedding inference error: %s", exc)
            raise EmbeddingServiceError(
                f"Embedding inference failed: {type(exc).__name__}",
                status_code=500,
            ) from exc
