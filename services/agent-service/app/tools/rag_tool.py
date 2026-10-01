import httpx

from app.domain.models import KnowledgeResult


class RagUnavailableError(RuntimeError):
    """Raised when Block 4 has no implemented query API to call."""


class UnavailableRagClient:
    """Honest local adapter until Block 4 publishes a query contract.

    The current Block 4 contains no API implementation, so this adapter must not
    guess an endpoint or fabricate retrieval results.
    """

    def __init__(self, service_url: str):
        self.service_url = service_url

    def search_knowledge(self, query: str) -> KnowledgeResult:
        raise RagUnavailableError(
            "No Block 4 query API adapter is configured."
        )


class HttpRagClient:
    """HTTP adapter for Block 4's published POST /rag/query contract."""

    def __init__(
        self,
        service_url: str,
        timeout_seconds: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ):
        self.base_url = service_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            transport=self.transport,
        )

    def is_ready(self) -> bool:
        try:
            with self._client() as client:
                response = client.get("/health/ready")
                return response.is_success
        except httpx.HTTPError:
            return False

    def search_knowledge(self, query: str) -> KnowledgeResult:
        try:
            with self._client() as client:
                response = client.post("/rag/query", json={"question": query})
                response.raise_for_status()
                body = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise RagUnavailableError("The local Block 4 query request failed.") from exc

        try:
            citations = []
            for item in body.get("citations", []):
                document_id = item["document_id"]
                source = item.get("source") or document_id
                citations.append(
                    {
                        "source": source,
                        "document_id": document_id,
                        "chunk_id": item["chunk_id"],
                        "page_number": item.get("page_number"),
                        "score": item["score"],
                        "metadata": {
                            "document_id": document_id,
                            "chunk_id": item["chunk_id"],
                            "page_number": item.get("page_number"),
                            "score": item["score"],
                        },
                    }
                )
            return KnowledgeResult(answer=body["answer"], citations=citations)
        except (KeyError, TypeError, ValueError) as exc:
            raise RagUnavailableError("The Block 4 query response did not match its API schema.") from exc
