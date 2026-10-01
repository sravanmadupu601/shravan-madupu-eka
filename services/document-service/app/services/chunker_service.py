"""Document chunking retained for migration into Block 2.

This module is intentionally not referenced by Block 1 upload or lifecycle
code. Move it with the ingestion implementation when Block 2 is created.
"""

class DocumentChunkerService:
    """Split extracted document text into overlapping chunks."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> list[str]:
        normalized_text = " ".join(
            text.split()
        )

        if not normalized_text:
            return []

        chunks = []

        start = 0
        text_length = len(normalized_text)

        while start < text_length:
            end = min(
                start + self.chunk_size,
                text_length,
            )

            chunk = normalized_text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            start = end - self.chunk_overlap

        return chunks