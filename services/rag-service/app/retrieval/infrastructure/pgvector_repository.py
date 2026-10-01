from app.retrieval.domain.models import RetrievalRequest, RetrievalResult


class PgVectorRepository:
    """Reserved adapter for a future verified PostgreSQL pgvector schema.

    Block 3 currently stores vectors as JSON and does not enable pgvector, so
    this adapter intentionally fails instead of loading vectors into Python or
    silently changing Block 3's schema.
    """

    def search(self, request: RetrievalRequest) -> list[RetrievalResult]:
        raise RuntimeError(
            "pgvector retrieval is not enabled: Block 3 currently stores embeddings as JSON."
        )
