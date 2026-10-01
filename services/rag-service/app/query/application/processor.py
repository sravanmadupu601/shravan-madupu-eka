from app.query.domain.models import Query


class DefaultQueryProcessor:
    def process(self, question: str) -> Query:
        return Query.create(question)
