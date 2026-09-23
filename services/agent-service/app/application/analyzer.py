import re

from app.domain.models import Intent, IntentAnalysis


_RESERVATION_ID = re.compile(
    r"\b(?:reservation\s+)?((?=[A-Z0-9]*\d)[A-Z0-9]{6,12})\b",
    re.IGNORECASE,
)
_BUSINESS_TERMS = re.compile(
    r"\b(reservation|booking|check[ -]?in|check[ -]?out|guest record|booking status)\b",
    re.IGNORECASE,
)
_KNOWLEDGE_TERMS = re.compile(
    r"\b(policy|policies|cancellation|cancel(?:lation)?|refund|penalty|deadline|"
    r"procedure|guideline|rules?|terms|eligib(?:le|ility)|how does|what is|explain)\b",
    re.IGNORECASE,
)


def analyze_request(query: str) -> IntentAnalysis:
    normalized = " ".join(query.split())
    has_reservation_id = bool(_RESERVATION_ID.search(normalized))
    requires_business = bool(_BUSINESS_TERMS.search(normalized) or has_reservation_id)
    requires_knowledge = bool(_KNOWLEDGE_TERMS.search(normalized))

    if requires_knowledge and requires_business:
        intent = Intent.KNOWLEDGE_AND_BUSINESS_DATA
    elif requires_knowledge:
        intent = Intent.KNOWLEDGE
    elif requires_business:
        intent = Intent.BUSINESS_DATA
    else:
        intent = Intent.GENERAL

    return IntentAnalysis(
        intent=intent,
        normalized_query=normalized,
        requires_rag=requires_knowledge,
        requires_business_data=requires_business,
    )
