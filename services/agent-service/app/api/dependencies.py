from functools import lru_cache

from app.application.agent_service import AgentService
from app.agent.graph import build_agent_graph
from app.config.settings import settings
from app.infrastructure.llm.mock_provider import MockLLMProvider
from app.tools.business_data_tool import LocalMockBusinessDataClient
from app.tools.rag_tool import HttpRagClient


@lru_cache(maxsize=1)
def get_agent_service() -> AgentService:
    if settings.llm_provider.lower() != "mock":
        raise ValueError("Only LLM_PROVIDER=mock is currently implemented.")
    retries = max(0, settings.max_agent_retries)
    graph = build_agent_graph(
        rag_client=HttpRagClient(settings.rag_service_url),
        business_data_client=LocalMockBusinessDataClient(),
        llm_provider=MockLLMProvider(),
        max_retries=retries,
    )
    return AgentService(runner=graph, max_retries=retries)
