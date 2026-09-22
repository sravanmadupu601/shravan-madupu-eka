import logging
from time import perf_counter

from app.citations.domain.models import CitationBuilder
from app.context.application.assembler import DefaultContextAssembler
from app.context.domain.models import ContextRequest
from app.embedding.domain.ports import QueryEmbeddingProvider
from app.generation.application.service import GenerationService
from app.generation.domain.models import GenerationRequest
from app.query.application.processor import DefaultQueryProcessor
from app.retrieval.application.retriever import DefaultRetriever
from app.retrieval.domain.models import RetrievalRequest
from app.reranking.application.pass_through import PassThroughReranker
from app.reranking.domain.models import RerankRequest

logger = logging.getLogger(__name__)


class RAGOrchestrator:
    def __init__(self, query_processor, embedding_provider: QueryEmbeddingProvider, retriever: DefaultRetriever, reranker: PassThroughReranker, context_assembler: DefaultContextAssembler, citation_builder: CitationBuilder, generation_service: GenerationService, default_top_k: int, similarity_threshold: float, max_context_characters: int):
        self.query_processor = query_processor
        self.embedding_provider = embedding_provider
        self.retriever = retriever
        self.reranker = reranker
        self.context_assembler = context_assembler
        self.citation_builder = citation_builder
        self.generation_service = generation_service
        self.default_top_k = default_top_k
        self.similarity_threshold = similarity_threshold
        self.max_context_characters = max_context_characters

    def execute(self, question: str, top_k: int | None = None, filters: dict[str, str] | None = None):
        started = perf_counter()
        query = self.query_processor.process(question)
        vector = self.embedding_provider.embed_query(query.normalized_text)
        retrieved = self.retriever.retrieve(RetrievalRequest(vector, top_k or self.default_top_k, self.similarity_threshold, filters or {}))
        reranked = self.reranker.rerank(RerankRequest(retrieved)).results
        context = self.context_assembler.build(ContextRequest(reranked, self.max_context_characters))
        citations = self.citation_builder.build(context.chunks)
        generated = self.generation_service.generate(GenerationRequest(query, context.text, citations))
        logger.info("RAG query completed: retrieved=%d context_characters=%d duration_ms=%.2f", len(retrieved), context.character_count, (perf_counter() - started) * 1000)
        return generated.answer, citations, len(retrieved)
