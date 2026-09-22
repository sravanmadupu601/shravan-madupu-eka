from typing import Protocol

from app.generation.domain.models import GenerationRequest, GenerationResponse


class LLMProvider(Protocol):
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        ...
