from typing import Protocol


class QueryEmbeddingProvider(Protocol):
    def embed_query(self, text: str) -> list[float]:
        ...

    def get_dimension(self) -> int:
        ...

    def get_model_name(self) -> str:
        ...
