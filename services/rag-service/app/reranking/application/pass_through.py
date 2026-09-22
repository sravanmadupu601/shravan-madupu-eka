from app.reranking.domain.models import RerankRequest, RerankResult


class PassThroughReranker:
    def rerank(self, request: RerankRequest) -> RerankResult:
        return RerankResult(sorted(request.results, key=lambda result: result.score, reverse=True))
