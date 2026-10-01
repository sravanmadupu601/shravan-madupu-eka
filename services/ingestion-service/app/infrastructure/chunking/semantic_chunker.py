from __future__ import annotations

import logging
import re
from typing import Protocol

import numpy as np

from app.services.chunker_service import TextChunk

logger = logging.getLogger(__name__)


class SentenceEmbeddingProvider(Protocol):
    def embed_sentences(self, sentences: list[str]) -> np.ndarray:
        ...


class SemanticChunker:
    def __init__(
        self,
        embedding_provider: SentenceEmbeddingProvider,
        similarity_threshold: float = 0.70,
        min_sentences: int = 1,
        max_sentences: int = 20,
    ):
        if not 0 <= similarity_threshold <= 1:
            raise ValueError("similarity_threshold must be between zero and one.")
        if min_sentences <= 0:
            raise ValueError("min_sentences must be greater than zero.")
        if max_sentences < min_sentences:
            raise ValueError("max_sentences must be greater than or equal to min_sentences.")
        self.embedding_provider = embedding_provider
        self.similarity_threshold = similarity_threshold
        self.min_sentences = min_sentences
        self.max_sentences = max_sentences

    def chunk(
        self,
        text: str,
        page_text: list[tuple[int | None, str]] | None = None,
    ) -> list[TextChunk]:
        if not text.strip():
            return []

        if page_text:
            chunks: list[TextChunk] = []
            for page_number, page_content in page_text:
                chunks.extend(self._chunk_text(page_content, page_number))
            return chunks
        return self._chunk_text(text, None)

    def _chunk_text(self, text: str, page_number: int | None) -> list[TextChunk]:
        sentences = self._split_sentences(text)
        if not sentences:
            return []
        if len(sentences) == 1:
            return [self._make_chunk(sentences, page_number)]

        logger.info("Semantic chunking started")
        logger.info("Sentence count: %d", len(sentences))
        embeddings = np.asarray(self.embedding_provider.embed_sentences(sentences))
        if embeddings.shape[0] != len(sentences):
            raise ValueError("Semantic embedding provider returned an unexpected result count.")
        if embeddings.ndim != 2:
            raise ValueError("Semantic embedding provider returned invalid embeddings.")

        chunks: list[TextChunk] = []
        current: list[str] = []
        boundaries = 0
        for index, sentence in enumerate(sentences):
            current.append(sentence)
            at_maximum = len(current) >= self.max_sentences
            is_last = index == len(sentences) - 1
            has_boundary = False
            if not is_last and not at_maximum:
                similarity = float(np.dot(embeddings[index], embeddings[index + 1]))
                has_boundary = similarity < self.similarity_threshold and len(current) >= self.min_sentences
            if at_maximum or has_boundary or is_last:
                chunks.append(self._make_chunk(current, page_number))
                if has_boundary:
                    boundaries += 1
                current = []

        logger.info("Semantic boundaries detected: %d", boundaries)
        logger.info("Semantic chunks generated: %d", len(chunks))
        return chunks

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return []
        return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", normalized) if sentence.strip()]

    @staticmethod
    def _make_chunk(sentences: list[str], page_number: int | None) -> TextChunk:
        content = " ".join(sentences).strip()
        return TextChunk(
            content=content,
            character_count=len(content),
            token_count=len(content.split()),
            page_number=page_number,
            sentence_count=len(sentences),
            chunking_strategy="semantic",
        )
