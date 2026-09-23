from dataclasses import dataclass
import re
from typing import Protocol


@dataclass(frozen=True)
class TextChunk:
    content: str
    character_count: int
    token_count: int
    page_number: int | None = None
    sentence_count: int | None = None
    chunking_strategy: str = "fixed"


class Chunker(Protocol):
    def chunk(
        self,
        text: str,
        page_text: list[tuple[int | None, str]] | None = None,
    ) -> list[TextChunk]:
        ...


class DocumentChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be non-negative and smaller than chunk_size.")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str, page_text: list[tuple[int | None, str]] | None = None) -> list[TextChunk]:
        if not text.strip():
            return []

        if page_text:
            chunks: list[TextChunk] = []
            for page_number, page_content in page_text:
                for chunk in self.chunk(page_content):
                    chunks.append(
                        TextChunk(
                            content=chunk.content,
                            character_count=chunk.character_count,
                            token_count=chunk.token_count,
                            page_number=page_number,
                            sentence_count=chunk.sentence_count,
                            chunking_strategy=chunk.chunking_strategy,
                        )
                    )
            return chunks

        chunks: list[TextChunk] = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            if end < len(text):
                boundary = text.rfind(" ", start, end)
                if boundary > start + self.chunk_size // 2:
                    end = boundary
            content = text[start:end].strip()
            if content:
                chunks.append(
                    TextChunk(
                        content=content,
                        character_count=len(content),
                        token_count=len(content.split()),
                        sentence_count=self._sentence_count(content),
                        chunking_strategy="fixed",
                    )
                )
            if end >= len(text):
                break
            start = max(end - self.chunk_overlap, start + 1)
        return chunks

    @staticmethod
    def _sentence_count(content: str) -> int:
        return max(1, len(re.findall(r"[^.!?]+(?:[.!?]+|$)", content)))
