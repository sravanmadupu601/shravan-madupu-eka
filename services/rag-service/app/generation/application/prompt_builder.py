from app.generation.domain.models import GenerationRequest


class PromptBuilder:
    def build(self, request: GenerationRequest) -> str:
        return (
            "Answer the question using only the supplied context. "
            "If the context is empty, say that no relevant context was found.\n\n"
            f"Question: {request.query.normalized_text}\n\n"
            f"Context:\n{request.context}"
        )
