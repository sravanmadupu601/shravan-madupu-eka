from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Chunk:
    content: str
    index: int
    metadata: dict[str, Any] = field(default_factory=dict)
