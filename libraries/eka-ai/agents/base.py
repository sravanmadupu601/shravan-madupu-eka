from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    """Contract for agent orchestration implementations."""

    @abstractmethod
    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
