from eka_ai.embeddings.base import EmbeddingProvider

from app.domain.exceptions import EmptyTextError


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """Local sentence-transformers adapter loaded lazily on first use."""

    def __init__(self, model_name: str, model_version: str, dimension: int):
        self._model_name = model_name
        self._model_version = model_version
        self._dimension = dimension
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
        return self._model

    def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            raise EmptyTextError("Cannot embed empty text.")
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if any(not text.strip() for text in texts):
            raise EmptyTextError("Cannot embed empty text.")
        vectors = self._get_model().encode(texts, convert_to_numpy=True).tolist()
        if any(len(vector) != self._dimension for vector in vectors):
            raise ValueError("Embedding provider returned an unexpected dimension.")
        return vectors

    def get_dimension(self) -> int:
        return self._dimension

    def get_model_name(self) -> str:
        return self._model_name

    def get_model_version(self) -> str:
        return self._model_version
