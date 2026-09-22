from typing import Protocol

from app.context.domain.models import Context, ContextRequest


class ContextAssembler(Protocol):
    def build(self, request: ContextRequest) -> Context:
        ...
