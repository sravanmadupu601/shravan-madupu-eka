# Service Boundaries

## Document Service

Answers: where is the document and what is its lifecycle?

It must not parse contents, chunk text, generate embeddings, perform retrieval, call LLMs, orchestrate agents, or expose MCP tools.

## Ingestion Service

Answers: what is inside the document and how should it be processed?

It reads originals through the configured local storage contract and owns parsed text, normalization, chunks, ingestion state, and processing metadata.

## Future boundaries

- Embedding Service: chunks to embeddings and vector persistence.
- RAG Service: retrieval, reranking, context assembly, citations, and local generation.
- Agent Service: orchestration, state, routing, retries, and approvals.
- MCP Service: controlled local tools, resources, prompts, and authorization.
- ML Service: isolated machine-learning experiments and inference.
- Data Analysis Service: structured data analysis and visualization.
- Evaluation Service: quality metrics, regression runs, and reports.

Services communicate through HTTP APIs and contracts. They do not import another service's internal Python modules or access another service's tables directly.
