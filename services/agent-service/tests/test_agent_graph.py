import pytest

from app.application.agent_service import AgentService
from app.agent.graph import build_agent_graph
from app.domain.models import AgentRequest, Intent, KnowledgeResult
from app.tools.rag_tool import RagUnavailableError
from tests.conftest import StubBusinessDataClient, StubLLMProvider, StubRagClient


def service(rag=None, business=None, llm=None, retries=2):
    graph = build_agent_graph(
        rag_client=rag or StubRagClient(),
        business_data_client=business or StubBusinessDataClient(),
        llm_provider=llm or StubLLMProvider(),
        max_retries=retries,
    )
    return AgentService(runner=graph, max_retries=retries)


def test_knowledge_only_request_propagates_citations(knowledge_result):
    rag = StubRagClient([knowledge_result])
    result = service(rag=rag).query(AgentRequest(query="What is the cancellation policy?"))
    assert result.intent == Intent.KNOWLEDGE
    assert result.tools_used == ["search_knowledge"]
    assert result.citations[0].source == "employee-policy.pdf"
    assert result.retry_count == 0
    assert result.validation_status == "SUFFICIENT"


def test_business_data_only_request_uses_read_only_mock(reservation):
    business = StubBusinessDataClient(reservation)
    result = service(business=business).query(
        AgentRequest(query="Show reservation ABC123 status")
    )
    assert result.intent == Intent.BUSINESS_DATA
    assert business.lookups == ["ABC123"]
    assert result.tools_used == ["get_reservation"]
    assert result.retry_count == 0


def test_knowledge_and_business_data_request_combines_tools(knowledge_result, reservation):
    rag = StubRagClient([knowledge_result])
    business = StubBusinessDataClient(reservation)
    result = service(rag=rag, business=business).query(
        AgentRequest(query="What is the cancellation policy for reservation ABC123?")
    )
    assert result.intent == Intent.KNOWLEDGE_AND_BUSINESS_DATA
    assert result.tools_used == ["search_knowledge", "get_reservation"]
    assert business.lookups == ["ABC123"]
    assert result.citations[0].source == "employee-policy.pdf"


def test_default_response_composer_combines_knowledge_and_local_data(knowledge_result, reservation):
    graph = build_agent_graph(
        rag_client=StubRagClient([knowledge_result]),
        business_data_client=StubBusinessDataClient(reservation),
        llm_provider=None,
        max_retries=2,
    )
    agent = AgentService(runner=graph, max_retries=2)
    result = agent.query(AgentRequest(query="What is the cancellation policy for reservation ABC123?"))
    assert "Cancellation requests must meet the stated deadline" in result.answer
    assert "Local demonstration reservation data" in result.answer


def test_general_request_skips_tools():
    rag = StubRagClient()
    business = StubBusinessDataClient()
    llm = StubLLMProvider()
    result = service(rag=rag, business=business, llm=llm).query(
        AgentRequest(query="Hello, what can you do?")
    )
    assert result.intent == Intent.GENERAL
    assert result.tools_used == []
    assert not rag.queries
    assert not business.lookups
    assert llm.calls == 1


def test_empty_retrieval_rewrites_and_retries_then_succeeds(knowledge_result):
    rag = StubRagClient([KnowledgeResult(), knowledge_result])
    result = service(rag=rag).query(AgentRequest(query="What is the cancellation policy?"))
    assert result.retry_count == 1
    assert len(rag.queries) == 2
    assert "deadline" in rag.queries[1]
    assert result.validation_status == "SUFFICIENT"


def test_retry_limit_is_bounded_and_no_citation_is_invented():
    rag = StubRagClient([KnowledgeResult(), KnowledgeResult(), KnowledgeResult(), KnowledgeResult()])
    result = service(rag=rag, retries=2).query(
        AgentRequest(query="What is the cancellation policy?")
    )
    assert result.retry_count == 2
    assert len(rag.queries) == 3
    assert result.validation_status == "INSUFFICIENT"
    assert result.citations == []


def test_validation_failure_without_rag_retry_for_missing_reservation():
    result = service().query(AgentRequest(query="Show reservation ABC123"))
    assert result.validation_status == "INSUFFICIENT"
    assert result.retry_count == 0
    assert result.citations == []


def test_missing_business_record_does_not_retry_successful_knowledge(knowledge_result):
    rag = StubRagClient([knowledge_result])
    result = service(rag=rag).query(
        AgentRequest(query="What is the cancellation policy for reservation XYZ999?")
    )
    assert result.validation_status == "INSUFFICIENT"
    assert result.retry_count == 0
    assert len(rag.queries) == 1


def test_business_tool_failure_is_reported_without_leaking_exception():
    result = service(business=StubBusinessDataClient(error=RuntimeError("private details"))).query(
        AgentRequest(query="Show reservation ABC123")
    )
    assert result.validation_status == "ERROR"
    assert "private details" not in result.answer
    assert result.warnings


def test_llm_failure_returns_safe_fallback():
    result = service(llm=StubLLMProvider(error=RuntimeError("private details"))).query(
        AgentRequest(query="Hello")
    )
    assert result.validation_status == "ERROR"
    assert "private details" not in result.answer
    assert result.warnings


def test_unavailable_rag_does_not_retry_or_fabricate_citations():
    rag = StubRagClient(error=RagUnavailableError("not connected"))
    result = service(rag=rag).query(AgentRequest(query="What is the cancellation policy?"))
    assert len(rag.queries) == 1
    assert result.retry_count == 0
    assert result.citations == []
    assert result.validation_status == "ERROR"
