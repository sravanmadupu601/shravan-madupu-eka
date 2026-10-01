from app.retrieval.domain.models import RetrievalRequest, RetrievalResult
from app.retrieval.domain.ports import VectorRepository


class DefaultRetriever:
    def __init__(self, repository: VectorRepository):
        self.repository = repository

    def retrieve(self, request: RetrievalRequest) -> list[RetrievalResult]:
        if request.top_k <= 0:
            raise ValueError("top_k must be greater than zero.")
        return self.repository.search(request)
