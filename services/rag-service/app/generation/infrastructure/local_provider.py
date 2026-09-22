from app.generation.domain.models import GenerationRequest, GenerationResponse


class DeterministicLocalProvider:
    """Local baseline provider; it does not call a hosted LLM."""

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        if not request.context:
            return GenerationResponse("No relevant context was found.")
        sources = ", ".join(str(c.chunk_id) for c in request.citations)
        return GenerationResponse(
            f"Local generation is configured. Relevant context was retrieved for "
            f"the question. Sources: {sources}."
        )
