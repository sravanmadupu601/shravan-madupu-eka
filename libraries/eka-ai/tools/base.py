from abc import ABC, abstractmethod
from typing import Any


class ToolProvider(ABC):
    """Contract for controlled local tools."""

    @abstractmethod
    def invoke(self, name: str, arguments: dict[str, Any]) -> Any:
        raise NotImplementedError
