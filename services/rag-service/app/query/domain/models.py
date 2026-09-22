from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Query:
    id: UUID
    text: str
    normalized_text: str
    created_at: datetime

    @classmethod
    def create(cls, text: str) -> "Query":
        normalized = " ".join(text.split())
        if not normalized:
            raise ValueError("Question must not be empty.")
        return cls(uuid4(), text, normalized, datetime.now(timezone.utc))
