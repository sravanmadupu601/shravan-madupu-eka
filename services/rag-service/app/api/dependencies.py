from app.citations.domain.models import CitationBuilder
from app.config.settings import settings
from app.context.application.assembler import DefaultContextAssembler
from app.embedding.infrastructure.sentence_transformer import SentenceTransformerQueryEmbeddingProvider
from app.generation.application.service import GenerationService
from app.generation.infrastructure.local_provider import DeterministicLocalProvider
from app.query.application.processor import DefaultQueryProcessor
from app.rag.application.orchestrator import RAGOrchestrator
from app.retrieval.application.retriever import DefaultRetriever
from app.retrieval.infrastructure.memory_repository import InMemoryVectorRepository
from app.reranking.application.pass_through import PassThroughReranker


_repository = InMemoryVectorRepository()
_provider = SentenceTransformerQueryEmbeddingProvider(
    settings.query_embedding_model_name,
    settings.query_embedding_dimension,
    settings.embedding_device,
)
_orchestrator = RAGOrchestrator(
    DefaultQueryProcessor(),
    _provider,
    DefaultRetriever(_repository),
    PassThroughReranker(),
    DefaultContextAssembler(),
    CitationBuilder(),
    GenerationService(DeterministicLocalProvider()),
    settings.default_top_k,
    settings.similarity_threshold,
    settings.max_context_characters,
)


def get_orchestrator() -> RAGOrchestrator:
    return _orchestrator
