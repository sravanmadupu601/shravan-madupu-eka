import uuid

from app.context.application.assembler import DefaultContextAssembler
from app.context.domain.models import ContextRequest
from app.retrieval.domain.models import RetrievalResult


def test_context_removes_duplicate_chunks_and_respects_limit():
    chunk_id = uuid.uuid4()
    result = RetrievalResult(uuid.uuid4(), chunk_id, "text", 0.9)
    context = DefaultContextAssembler().build(ContextRequest([result, result], 1000))

    assert len(context.chunks) == 1
    assert context.text.count("text") == 1
