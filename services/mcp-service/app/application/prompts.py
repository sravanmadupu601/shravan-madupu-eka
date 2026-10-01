def enterprise_knowledge_query(
    query: str,
    response_style: str = "concise",
    citation_required: bool = True,
) -> str:
    style = response_style.strip() or "concise"
    citations = "Include citations for every enterprise-knowledge claim; never invent citations." if citation_required else "Preserve any available citations and never invent them."
    return (
        "Answer the user's question using retrieved EKA enterprise knowledge where required. "
        "If the available information does not answer the question, clearly say so instead of guessing. "
        f"{citations} Use a {style} response style.\n\nQuestion: {query.strip()}"
    )
