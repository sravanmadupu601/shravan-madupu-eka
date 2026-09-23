from fastapi import FastAPI

from app.api.routes.agent import router as agent_router
from app.config.settings import settings
from app.tools.rag_tool import HttpRagClient

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(agent_router)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/ready", tags=["Health"])
def readiness() -> dict[str, object]:
    rag_ready = HttpRagClient(settings.rag_service_url).is_ready()
    return {
        "status": "ready",
        "agent_graph": "available",
        "llm_provider": settings.llm_provider,
        "rag_integration": "available" if rag_ready else "unavailable",
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
        "rag_api": "POST /rag/query",
        "llm_provider": settings.llm_provider,
    }
