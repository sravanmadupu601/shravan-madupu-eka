from app.domain.models import AgentRequest, AgentResponse, Citation
from app.domain.ports import AgentRunner


class AgentService:
    def __init__(
        self,
        runner: AgentRunner,
        max_retries: int,
    ):
        self.max_retries = max(0, max_retries)
        self.runner = runner

    def query(self, request: AgentRequest) -> AgentResponse:
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
        return AgentResponse(
            answer=result["answer"],
            intent=result["intent"],
            route=result["route"],
            citations=[Citation.model_validate(item) for item in result["citations"]],
            tools_used=result["tools_used"],
            retry_count=result["retry_count"],
            validation_status=result["validation_status"],
            warnings=result["warnings"],
        )
