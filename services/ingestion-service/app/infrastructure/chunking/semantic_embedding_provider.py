from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


class HuggingFaceSemanticEmbeddingProvider:
    """Lazily loads a local Sentence Transformer model once per process."""

    def __init__(self, model_name: str, device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self._model = None

    def embed_sentences(self, sentences: list[str]) -> np.ndarray:
        if not sentences:
            return np.empty((0, 0), dtype=np.float32)
        if self._model is None:
            logger.info("Loading semantic embedding model: %s", self.model_name)
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name, device=self.device)
            except Exception as exc:
                raise RuntimeError(
                    f"Unable to load semantic embedding model '{self.model_name}'."
                ) from exc
            logger.info("Semantic embedding model loaded")

        try:
            return self._model.encode(
                sentences,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
        except Exception as exc:
            raise RuntimeError("Unable to generate semantic sentence embeddings.") from exc
