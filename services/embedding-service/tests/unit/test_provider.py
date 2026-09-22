from app.domain.exceptions import EmptyTextError
from app.infrastructure.embeddings.sentence_transformer_provider import SentenceTransformerEmbeddingProvider


def test_provider_metadata_is_configurable():
    provider = SentenceTransformerEmbeddingProvider("local-test", "v2", 3)
    assert provider.get_model_name() == "local-test"
    assert provider.get_model_version() == "v2"
    assert provider.get_dimension() == 3


def test_provider_rejects_empty_text_without_loading_model():
    provider = SentenceTransformerEmbeddingProvider("local-test", "v1", 3)
    try:
        provider.embed_text("")
        assert False
    except EmptyTextError:
        assert True


def test_fake_provider_returns_expected_vectors(provider):
    assert len(provider.embed_text("hello")) == 3
    assert len(provider.embed_texts(["one", "two"])) == 2
