# EKA RAG Service

Block 4 is one local FastAPI service containing separate folders for query processing, query embedding, retrieval, reranking, context assembly, citations, and generation. The folders are independent architecture boundaries; they are not seven servers.

## Current flow

```text
Question
	-> Query normalization
	-> Temporary 384-D query embedding
	-> VectorRepository / Retriever
	-> Deterministic reranking
	-> Bounded context assembly
	-> Citation building
	-> Local deterministic generation
	-> Answer
```

Block 2 produces chunks. Block 3 produces persistent chunk embeddings. Block 4 consumes the vector-store contract. Block 3 currently stores vectors as JSON and does not expose a similarity-search API or pgvector column, so this service does not silently read Block 3 internals or claim PostgreSQL vector search is enabled.

## Retrieval status

The technology-independent `VectorRepository` and `Retriever` contracts are implemented. The default local adapter is `InMemoryVectorRepository`, which supports cosine scoring for explicitly supplied local vectors and is used by tests/development. `PgVectorRepository` is an explicit boundary that reports pgvector is not enabled. It does not load all Block 3 JSON vectors into Python.

A future verified pgvector migration must be separate from Block 3 and define a `VECTOR(384)` column plus the PostgreSQL `vector` extension before the pgvector adapter is enabled.

## API

- `GET /health`
- `GET /ready`
- `GET /info`
- `POST /rag/query`

Example:

```json
{
	"question": "What is our deployment process?",
	"top_k": 5
}
```

The initial generation provider is local and deterministic. It is an abstraction point, not an LLM implementation and not a cloud dependency.

## Configuration

Copy `.env.example` to `.env` and configure local values. The query model defaults to `sentence-transformers/all-MiniLM-L6-v2` on CPU. Query embeddings are temporary and are never persisted by Block 4.

`VECTOR_BACKEND=memory` is the only verified backend in this implementation. No credentials are required for the default test/local flow.

## Run locally

```powershell
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8003
```

Run tests:

```powershell
python -m pytest -q
```

## Responsibilities

- `query/`: validation and normalization.
- `embedding/`: temporary query embedding provider abstraction and local Sentence Transformer adapter.
- `retrieval/`: vector repository/retriever contracts, in-memory adapter, and pgvector boundary.
- `reranking/`: deterministic baseline reranker.
- `context/`: deduplication, ordering, metadata-preserving context limits.
- `citations/`: source and chunk attribution.
- `generation/`: prompt/generation contracts and local baseline provider.
- `rag/`: application orchestration only.

No Block 1, Block 2, or Block 3 Python modules are imported. No Block 4 database migration is created because this implementation owns no tables yet.
