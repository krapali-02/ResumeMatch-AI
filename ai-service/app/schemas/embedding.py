"""Embedding request and response schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class EmbeddingRequest(BaseModel):
    """Request payload for dense semantic vector generation."""

    text: Optional[str] = Field(
        default=None,
        description="Single text string to encode into a 384-dimensional vector",
    )
    texts: Optional[List[str]] = Field(
        default=None,
        description="Batch of text strings to encode into 384-dimensional vectors",
    )

    @model_validator(mode="after")
    def validate_inputs(self) -> "EmbeddingRequest":
        has_text = self.text is not None and bool(self.text.strip())
        has_texts = self.texts is not None and len(self.texts) > 0

        if not has_text and not has_texts:
            raise ValueError("Either 'text' (non-empty) or 'texts' (non-empty list) must be provided.")

        if self.texts is not None:
            if len(self.texts) == 0:
                raise ValueError("'texts' cannot be an empty list.")
            for idx, item in enumerate(self.texts):
                if not isinstance(item, str) or not item.strip():
                    raise ValueError(f"Batch item at index {idx} must be a non-empty string.")

        return self


class EmbeddingResponse(BaseModel):
    """Dense vector embedding response payload."""

    model: str = Field(description="Name and version of the Sentence Transformer model")
    dimensions: int = Field(default=384, description="Vector dimensionality (strictly 384)")
    embeddings: List[List[float]] = Field(description="List of L2-normalized 384-dimensional vector arrays")
    normalized: bool = Field(default=True, description="Indicates whether embeddings are L2 unit normalized")
    count: int = Field(description="Number of embeddings generated")
