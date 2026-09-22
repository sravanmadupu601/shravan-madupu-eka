from typing import Protocol

from app.query.domain.models import Query


class QueryProcessor(Protocol):
    def process(self, question: str) -> Query:
        ...
