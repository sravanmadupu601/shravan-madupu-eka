from app.context.domain.models import Context, ContextRequest


class DefaultContextAssembler:
    def build(self, request: ContextRequest) -> Context:
        if request.max_characters <= 0:
            raise ValueError("max_characters must be greater than zero.")
        selected = []
        seen = set()
        parts = []
        size = 0
        for result in request.results:
            if result.chunk_id in seen:
                continue
            prefix = f"[Source: {result.source or result.document_id} | Chunk: {result.chunk_id}]\n"
            part = prefix + result.text
            if size + len(part) > request.max_characters:
                break
            seen.add(result.chunk_id)
            selected.append(result)
            parts.append(part)
            size += len(part) + 2
        return Context("\n\n".join(parts), selected, size)
