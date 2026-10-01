from fastapi import APIRouter, Depends

from app.api.dependencies import get_agent_service
from app.application.agent_service import AgentService
from app.domain.models import AgentRequest, AgentResponse

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/query", response_model=AgentResponse)
def query_agent(
    request: AgentRequest,
    service: AgentService = Depends(get_agent_service),
) -> AgentResponse:
    return service.query(request)
