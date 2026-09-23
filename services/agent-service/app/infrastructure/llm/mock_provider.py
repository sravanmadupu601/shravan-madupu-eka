from typing import Any

from app.domain.models import KnowledgeResult


class MockLLMProvider:
    """Deterministic local response composer with no external model calls."""

    def generate(
        self,
        *,
        query: str,
        intent: str,
        knowledge: KnowledgeResult | None,
        business_data: dict[str, Any] | None,
        warnings: list[str],
    ) -> str:
        sections: list[str] = []
        if knowledge and knowledge.answer:
            sections.append(f"Knowledge-base information: {knowledge.answer}")
        elif knowledge and knowledge.documents:
            texts = [str(item.get("text", "")).strip() for item in knowledge.documents]
            texts = [text for text in texts if text]
            if texts:
                sections.append("Knowledge-base information: " + " ".join(texts))

        if business_data:
            fields = [
                f"{key.replace('_', ' ')}: {value}"
                for key, value in business_data.items()
                if key != "data_source"
            ]
            sections.append("Local demonstration reservation data: " + "; ".join(fields))

        if warnings and not sections:
            sections.append(
                "I could not retrieve the requested knowledge because the local RAG "
                "service is unavailable. No knowledge-base answer "
                "or citation is available."
            )
        elif intent in {"KNOWLEDGE", "KNOWLEDGE_AND_BUSINESS_DATA"} and not knowledge:
            sections.append(
                "No relevant knowledge-base information was returned after the "
                "configured retrieval attempts. I cannot provide a sourced policy answer."
            )
        elif not sections:
            sections.append(
                "I can help with knowledge-base questions and read-only reservation "
                "lookups. This local service uses deterministic request routing and "
                "a mock response provider; it does not call a language model."
            )
        return "\n\n".join(sections)
