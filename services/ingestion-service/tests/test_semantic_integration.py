import os

import pytest

from app.infrastructure.chunking.semantic_chunker import SemanticChunker
from app.infrastructure.chunking.semantic_embedding_provider import HuggingFaceSemanticEmbeddingProvider


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("RUN_SEMANTIC_INTEGRATION") != "1",
    reason="Set RUN_SEMANTIC_INTEGRATION=1 to download/load the local model.",
)
def test_local_sentence_transformer_integration():
    provider = HuggingFaceSemanticEmbeddingProvider(
        "sentence-transformers/all-MiniLM-L6-v2",
        "cpu",
    )
    embeddings = provider.embed_sentences(["A local sentence.", "Another local sentence."])
    assert embeddings.shape == (2, 384)

    chunks = SemanticChunker(provider).chunk(
        "A local sentence. Another local sentence."
    )
    assert chunks
