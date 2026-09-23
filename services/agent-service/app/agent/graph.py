from typing import Literal
import json

from langgraph.graph import END, START, StateGraph

from app.agent.state import AgentState
from app.domain.models import Intent, KnowledgeResult
from app.domain.ports import BusinessDataClient, LLMProvider, RagClient
from app.infrastructure.llm.mock_provider import MockLLMProvider
from app.tools.business_data_tool import LocalMockBusinessDataClient
from app.tools.rag_tool import RagUnavailableError


def build_agent_graph(
    rag_client: RagClient,
    business_data_client: BusinessDataClient,
    llm_provider: LLMProvider | None = None,
    max_retries: int = 2,
):
    provider = llm_provider or MockLLMProvider()

    def analyze_node(state: AgentState) -> dict:
        from app.application.analyzer import analyze_request

        analysis = analyze_request(state["user_query"])
        return {
            "normalized_query": analysis.normalized_query,
            "intent": analysis.intent.value,
            "requires_rag": analysis.requires_rag,
            "requires_business_data": analysis.requires_business_data,
        }

    def route_node(state: AgentState) -> dict:
        return {"route": state["intent"]}

    def retrieve_node(state: AgentState) -> dict:
        query = state.get("rewritten_query") or state["normalized_query"]
        tools = list(state["tools_used"])
        if "search_knowledge" not in tools:
            tools.append("search_knowledge")
        try:
            result = rag_client.search_knowledge(query)
        except RagUnavailableError:
            return {
                "tools_used": tools,
                "errors": [*state["errors"], "RAG_UNAVAILABLE"],
                "warnings": [
                    *state["warnings"],
                    "The local Block 4 query API is unavailable; knowledge retrieval failed.",
                ],
            }
        except Exception:
            return {
                "tools_used": tools,
                "errors": [*state["errors"], "RAG_REQUEST_FAILED"],
                "warnings": [*state["warnings"], "The local knowledge service request failed."],
            }
        if not isinstance(result, KnowledgeResult):
            result = KnowledgeResult.model_validate(result)
        return {
            "tools_used": tools,
            "knowledge_answer": result.answer,
            "retrieved_documents": result.documents,
            "citations": [citation.model_dump() for citation in result.citations],
            "context": "\n".join(
                [result.answer or "", *(str(doc.get("text", "")) for doc in result.documents)]
            ).strip(),
        }

    def execute_tool_node(state: AgentState) -> dict:
        import re

        match = re.search(
            r"\b(?:reservation\s+)?((?=[A-Z0-9]*\d)[A-Z0-9]{6,12})\b",
            state["normalized_query"],
            re.I,
        )
        if not match:
            return {
                "errors": [*state["errors"], "RESERVATION_ID_MISSING"],
                "warnings": [*state["warnings"], "No reservation identifier was found in the request."],
            }
        tools = list(state["tools_used"])
        if "get_reservation" not in tools:
            tools.append("get_reservation")
        try:
            record = business_data_client.get_reservation(match.group(1))
        except Exception:
            return {
                "tools_used": tools,
                "errors": [*state["errors"], "BUSINESS_DATA_REQUEST_FAILED"],
                "warnings": [*state["warnings"], "The local business-data lookup failed."],
            }
        if record is None:
            return {
                "tools_used": tools,
                "tool_results": {**state["tool_results"], "reservation": None},
                "warnings": [*state["warnings"], "No local mock reservation matched that identifier."],
            }
        return {
            "tools_used": tools,
            "tool_results": {**state["tool_results"], "reservation": record},
            "context": "\n".join(
                part
                for part in (
                    state["context"],
                    "Business data (LOCAL MOCK DATA): " + json.dumps(record, sort_keys=True),
                )
                if part
            ),
        }

    def validate_node(state: AgentState) -> dict:
        if state["errors"]:
            return {"validation_status": "ERROR"}
        if state["requires_rag"] and not (
            state["knowledge_answer"] or state["retrieved_documents"]
        ):
            return {"validation_status": "INSUFFICIENT"}
        if state["requires_business_data"] and not state["tool_results"].get("reservation"):
            return {"validation_status": "INSUFFICIENT"}
        return {"validation_status": "SUFFICIENT"}

    def rewrite_node(state: AgentState) -> dict:
        query = state["normalized_query"]
        if "cancel" in query.lower():
            rewritten = f"{query} cancellation policy deadline eligibility exceptions applicable penalty"
        else:
            rewritten = f"{query} requirements rules definitions relevant exceptions"
        return {
            "rewritten_query": " ".join(rewritten.split()),
            "retry_count": state["retry_count"] + 1,
        }

    def generate_node(state: AgentState) -> dict:
        business = state["tool_results"].get("reservation")
        knowledge = KnowledgeResult(
            answer=state["knowledge_answer"],
            documents=state["retrieved_documents"],
            citations=state["citations"],
        ) if state["knowledge_answer"] or state["retrieved_documents"] or state["citations"] else None
        try:
            answer = provider.generate(
                query=state["user_query"],
                intent=state["intent"],
                knowledge=knowledge,
                business_data=business,
                warnings=state["warnings"],
            )
        except Exception:
            answer = "I could not generate a response because the configured local response provider failed."
            return {
                "answer": answer,
                "validation_status": "ERROR",
                "errors": [*state["errors"], "LLM_PROVIDER_FAILED"],
                "warnings": [*state["warnings"], "The configured local response provider failed."],
            }
        return {
            "answer": answer,
            "validation_status": (
                "SUFFICIENT" if state["validation_status"] == "PENDING" else state["validation_status"]
            ),
        }

    def choose_route(state: AgentState) -> Literal["knowledge", "business", "general"]:
        if state["intent"] in (Intent.KNOWLEDGE.value, Intent.KNOWLEDGE_AND_BUSINESS_DATA.value):
            return "knowledge"
        if state["intent"] == Intent.BUSINESS_DATA.value:
            return "business"
        return "general"

    def after_retrieval(state: AgentState) -> Literal["business", "validate"]:
        if state["intent"] == Intent.KNOWLEDGE_AND_BUSINESS_DATA.value and state["retry_count"] == 0:
            return "business"
        return "validate"

    def after_validation(state: AgentState) -> Literal["rewrite", "respond"]:
        if (
            state["validation_status"] == "INSUFFICIENT"
            and state["requires_rag"]
            and not (state["knowledge_answer"] or state["retrieved_documents"])
            and state["retry_count"] < state["max_retries"]
        ):
            return "rewrite"
        return "respond"

    graph = StateGraph(AgentState)
    graph.add_node("analyze_request", analyze_node)
    graph.add_node("route_request", route_node)
    graph.add_node("retrieve_knowledge", retrieve_node)
    graph.add_node("execute_tool", execute_tool_node)
    graph.add_node("validate_results", validate_node)
    graph.add_node("rewrite_query", rewrite_node)
    graph.add_node("generate_response", generate_node)
    graph.add_edge(START, "analyze_request")
    graph.add_edge("analyze_request", "route_request")
    graph.add_conditional_edges(
        "route_request",
        choose_route,
        {"knowledge": "retrieve_knowledge", "business": "execute_tool", "general": "generate_response"},
    )
    graph.add_conditional_edges(
        "retrieve_knowledge",
        after_retrieval,
        {"business": "execute_tool", "validate": "validate_results"},
    )
    graph.add_edge("execute_tool", "validate_results")
    graph.add_conditional_edges(
        "validate_results",
        after_validation,
        {"rewrite": "rewrite_query", "respond": "generate_response"},
    )
    graph.add_edge("rewrite_query", "retrieve_knowledge")
    graph.add_edge("generate_response", END)
    return graph.compile()


def create_default_graph(rag_service_url: str, max_retries: int = 2):
    from app.tools.rag_tool import UnavailableRagClient

    return build_agent_graph(
        rag_client=UnavailableRagClient(rag_service_url),
        business_data_client=LocalMockBusinessDataClient(),
        max_retries=max_retries,
    )
