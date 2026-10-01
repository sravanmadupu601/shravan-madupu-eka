from abc import ABC, abstractmethod
from collections.abc import Sequence

from .models import Chunk


class Chunker(ABC):
    """EKA-owned contract for deterministic or semantic chunking strategies."""

    @abstractmethod
    def chunk(self, text: str) -> Sequence[Chunk]:
        raise NotImplementedError
