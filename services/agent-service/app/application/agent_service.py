import logging
from time import perf_counter

from app.domain.models import AgentRequest, AgentResponse, Citation
from app.domain.ports import AgentRunner

logger = logging.getLogger(__name__)


class AgentService:
    def __init__(
        self,
        runner: AgentRunner,
        max_retries: int,
    ):
        self.max_retries = min(max(0, max_retries), 2)
        self.runner = runner

    def query(self, request: AgentRequest) -> AgentResponse:
        started = perf_counter()
        initial_state = {
            "user_query": request.query,
            "normalized_query": request.query,
            "intent": "GENERAL",
            "route": "GENERAL",
            "requires_rag": False,
            "requires_business_data": False,
            "rewritten_query": None,
            "retrieved_documents": [],
            "knowledge_answer": None,
            "tool_results": {},
            "citations": [],
            "context": "",
            "answer": "",
            "retry_count": 0,
            "max_retries": self.max_retries,
            "validation_status": "PENDING",
            "errors": [],
            "warnings": [],
            "tools_used": [],
        }
        result = self.runner.invoke(
            initial_state,
            config={"recursion_limit": max(20, self.max_retries * 5 + 12)},
        )
        response = AgentResponse(
            answer=result["answer"],
            intent=result["intent"],
            route=result["route"],
            citations=[Citation.model_validate(item) for item in result["citations"]],
            tools_used=result["tools_used"],
            retry_count=result["retry_count"],
            validation_status=result["validation_status"],
            warnings=result["warnings"],
        )
        logger.info(
            "Agent query completed: intent=%s route=%s tools=%s retries=%d status=%s duration_ms=%.2f",
            response.intent.value,
            response.route,
            ",".join(response.tools_used),
            response.retry_count,
            response.validation_status,
            (perf_counter() - started) * 1000,
        )
        return response
