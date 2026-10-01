import numpy as np

from app.infrastructure.chunking.semantic_chunker import SemanticChunker


class FakeEmbeddingProvider:
    def __init__(self, embeddings):
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.calls = []

    def embed_sentences(self, sentences):
        self.calls.append(sentences)
        return self.embeddings


def test_empty_text_returns_no_chunks_without_embedding():
    provider = FakeEmbeddingProvider([])
    assert SemanticChunker(provider).chunk(" ") == []
    assert provider.calls == []


def test_similar_sentences_stay_together_and_provider_is_batched():
    provider = FakeEmbeddingProvider([[1, 0], [0.99, 0.01], [0.98, 0.02]])
    chunks = SemanticChunker(provider, similarity_threshold=0.70).chunk(
        "Alpha topic. Alpha detail. Alpha conclusion."
    )

    assert len(chunks) == 1
    assert provider.calls == [["Alpha topic.", "Alpha detail.", "Alpha conclusion."]]
    assert chunks[0].sentence_count == 3
    assert chunks[0].chunking_strategy == "semantic"
    assert chunks[0].character_count == len(chunks[0].content)


def test_low_similarity_creates_boundary():
    provider = FakeEmbeddingProvider([[1, 0], [1, 0], [0, 1]])
    chunks = SemanticChunker(provider, similarity_threshold=0.70).chunk(
        "Alpha topic. Alpha detail. Unrelated topic."
    )

    assert [chunk.sentence_count for chunk in chunks] == [2, 1]


def test_similarity_equal_to_threshold_stays_in_same_chunk():
    provider = FakeEmbeddingProvider([[1, 0], [0.5, 0]])
    chunks = SemanticChunker(provider, similarity_threshold=0.50).chunk(
        "First topic. Second topic."
    )

    assert len(chunks) == 1


def test_maximum_sentence_limit_splits_chunks_sequentially():
    provider = FakeEmbeddingProvider([[1, 0]] * 5)
    chunks = SemanticChunker(provider, max_sentences=2).chunk(
        "One. Two. Three. Four. Five."
    )

    assert [chunk.sentence_count for chunk in chunks] == [2, 2, 1]


def test_one_sentence_does_not_require_model_embeddings():
    provider = FakeEmbeddingProvider([])
    chunks = SemanticChunker(provider).chunk("One sentence only.")

    assert len(chunks) == 1
    assert provider.calls == []