from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from app.application.prompts import enterprise_knowledge_query as build_enterprise_knowledge_query
from app.application.service import MCPApplicationService


def create_mcp_server(service: MCPApplicationService, name: str, host: str, port: int) -> FastMCP:
    server = FastMCP(
        name=name,
        instructions=(
            "Local EKA integration adapter. Use the explicit EKA tools for knowledge search "
            "and read-only document metadata. The server does not expose arbitrary files, shell, or database access."
        ),
        host=host,
        port=port,
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=[
                "127.0.0.1",
                "127.0.0.1:*",
                "localhost",
                "localhost:*",
                "[::1]",
                "[::1]:*",
            ],
            allowed_origins=["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"],
        ),
    )

    @server.tool()
    def search_knowledge(query: str, top_k: int = 5) -> dict[str, Any]:
        """Search enterprise knowledge through Block 4 RAG.

        Use for policy, procedure, and knowledge-base questions. Input is a query
        and top_k between 1 and 100. Output contains the answer, retrieved count,
        and Block 4 citations. Retrieval logic remains in Block 4.
        """
        return service.search_knowledge(query, top_k)

    @server.tool()
    def get_document(document_id: str) -> dict[str, Any]:
        """Get safe document metadata from Block 1 by UUID.

        Use when the caller needs a document's name, type, size, status, checksum,
        or timestamps. Does not return file contents or storage paths.
        """
        return service.get_document(document_id)

    @server.tool()
    def list_documents(limit: int = 50, offset: int = 0) -> dict[str, Any]:
        """List safe document metadata from Block 1 with pagination.

        Limit must be 1..100 and offset non-negative. Does not access the database directly.
        """
        return service.list_documents(limit, offset)

    @server.tool()
    def document_health() -> dict[str, Any]:
        """Check Block 1 Document Service readiness over its local HTTP API."""
        return service.document_health()

    @server.tool()
    def rag_health() -> dict[str, Any]:
        """Check Block 4 RAG Service readiness over its local HTTP API."""
        return service.rag_health()

    @server.resource("eka://documents")
    def documents_resource() -> str:
        """Read a page of safe document metadata from Block 1; no file contents are exposed."""
        return service.documents_resource()

    @server.prompt(title="Enterprise Knowledge Query")
    def enterprise_knowledge_query(
        query: str,
        response_style: str = "concise",
        citation_required: str = "required",
    ) -> str:
        """Build a grounded prompt. citation_required accepts 'required' or 'optional'."""
        citation_setting = citation_required.strip().lower()
        if citation_setting not in {"required", "optional"}:
            raise ValueError("citation_required must be 'required' or 'optional'.")
        return build_enterprise_knowledge_query(
            query,
            response_style,
            citation_setting == "required",
        )

    return server
