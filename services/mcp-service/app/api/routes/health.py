from fastapi import APIRouter

from app.config.settings import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/ready")
def ready() -> dict[str, str | int]:
    return {
        "status": "ready",
        "transport": "streamable-http",
        "mcp_endpoint": "/mcp",
        "port": settings.mcp_service_port,
    }


@router.get("/info")
def info() -> dict[str, object]:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "port": settings.mcp_service_port,
        "transport": "streamable-http",
        "mcp_endpoint": "/mcp",
        "tools": ["search_knowledge", "get_document", "list_documents", "document_health", "rag_health"],
        "resources": ["eka://documents"],
        "prompts": ["enterprise_knowledge_query_prompt"],
    }
