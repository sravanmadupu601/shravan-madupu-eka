from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Contract for local language-model providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError
