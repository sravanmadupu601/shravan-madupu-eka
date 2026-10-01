from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any


class Retriever(ABC):
    """Contract for retrieval implementations."""

    @abstractmethod
    def retrieve(self, query: str, *, limit: int = 10) -> Sequence[dict[str, Any]]:
        raise NotImplementedError
