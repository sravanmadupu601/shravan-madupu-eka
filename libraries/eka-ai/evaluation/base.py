from abc import ABC, abstractmethod
from typing import Any


class Evaluator(ABC):
    """Contract for evaluation strategies and metrics."""

    @abstractmethod
    def evaluate(self, input_data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
