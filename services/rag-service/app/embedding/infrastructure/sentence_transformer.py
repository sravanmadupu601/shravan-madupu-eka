from __future__ import annotations

from app.embedding.domain.ports import QueryEmbeddingProvider


class SentenceTransformerQueryEmbeddingProvider:
    def __init__(self, model_name: str, dimension: int, device: str = "cpu"):
        self.model_name = model_name
        self.dimension = dimension
        self.device = device
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model

    def embed_query(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Query text must not be empty.")
        vector = self._get_model().encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0].tolist()
        if len(vector) != self.dimension:
            raise ValueError("Query embedding has an unexpected dimension.")
        return vector

    def get_dimension(self) -> int:
        return self.dimension

    def get_model_name(self) -> str:
        return self.model_name
