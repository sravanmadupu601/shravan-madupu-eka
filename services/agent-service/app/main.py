from fastapi import FastAPI

from app.api.routes.agent import router as agent_router
from app.config.settings import settings
from app.tools.mcp_client import StreamableHttpMCPClient

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(agent_router)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/ready", tags=["Health"])
def readiness() -> dict[str, object]:
    mcp_ready = StreamableHttpMCPClient(settings.mcp_service_url).is_ready()
    return {
        "status": "ready",
        "agent_graph": "available",
        "llm_provider": settings.llm_provider,
        "mcp_integration": "available" if mcp_ready else "unavailable",
        "rag_integration": "through_mcp",
    }


@app.get("/info", tags=["Health"])
def info() -> dict[str, object]:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "port": settings.agent_service_port,
        "graph_nodes": [
            "analyze_request",
            "route_request",
            "retrieve_knowledge",
            "execute_tool",
            "validate_results",
            "rewrite_query",
            "generate_response",
        ],
        "features": ["deterministic_routing", "local_mock_business_data", "bounded_retries"],
        "mcp_server": settings.mcp_service_url,
        "llm_provider": settings.llm_provider,
    }
