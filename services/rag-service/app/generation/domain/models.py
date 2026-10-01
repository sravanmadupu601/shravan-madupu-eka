from dataclasses import dataclass

from app.citations.domain.models import Citation
from app.query.domain.models import Query


@dataclass(frozen=True)
class GenerationRequest:
    query: Query
    context: str
    citations: list[Citation]


@dataclass(frozen=True)
class GenerationResponse:
    answer: str
