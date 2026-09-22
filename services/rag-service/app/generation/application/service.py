from app.generation.domain.models import GenerationRequest, GenerationResponse
from app.generation.domain.ports import LLMProvider


class GenerationService:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        return self.provider.generate(request)
