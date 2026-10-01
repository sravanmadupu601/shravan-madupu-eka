# EKA Embedding Service

Block 3 receives chunks through an API, generates local embeddings, persists
embedding metadata and vectors, and supports deterministic reprocessing.

## Architecture

The API depends on `EmbeddingApplicationService`, which depends on the
EKA-owned `EmbeddingProvider` and `EmbeddingRepository` abstractions. The
default adapters are `SentenceTransformerEmbeddingProvider` and
`PostgresEmbeddingRepository`.

Block 3 does not import Block 1 or Block 2 Python modules and does not read
their databases. Chunk data arrives through the API contract.

## API

- `POST /embeddings` accepts a document ID and chunk IDs/text, returning embedding metadata.
- `GET /embeddings/{document_id}` returns persisted embedding metadata for a document.
- `GET /health`, `/health/live`, `/health/ready`, and `/health/db` expose health checks.

Vectors are intentionally not returned by the generation API. PostgreSQL
stores them as `VECTOR(384)` through pgvector. The domain layer still uses
`list[float]`; pgvector is confined to the infrastructure model and repository.

## Local model

The default provider uses the local `sentence-transformers/all-MiniLM-L6-v2`
model through `sentence-transformers` and PyTorch. Model name, version, and
dimension are configured through environment variables. The model is loaded
lazily on the first real embedding request.

## Database and idempotency

The `embeddings` table stores document ID, chunk ID, vector, model metadata,
dimension, and timestamps. A unique constraint on document, chunk, model name,
and model version makes repeated requests reuse existing embeddings. A changed
model version creates a new record.

Migration `002` enables the local PostgreSQL `vector` extension, validates
existing JSON arrays, converts them to `VECTOR(384)` without changing row IDs
or metadata, and adds an HNSW cosine-distance index. The migration does not
drop existing values before conversion. For small local datasets, the index
may not show a measurable benefit yet, but it provides the intended production
query path.

Similarity search is performed by PostgreSQL with pgvector's cosine-distance
operator (`<=>`) through `PostgresEmbeddingRepository.search_similar()`. It
supports top-K, similarity thresholds, and document/model filters. The API is
`POST /embeddings/search`; query vectors are temporary and are not persisted.

Block 3 owns an independent Alembic history using the
`embedding_alembic_version` table.

## Configuration

Copy `.env.example` to `.env` and set a local PostgreSQL `DATABASE_URL`.
Never commit `.env` or credentials.

## Running locally

```powershell
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

Run tests with:

```powershell
python -m pytest -v
```

Verify manually after installing the declared dependency and having a local
PostgreSQL instance with pgvector available:

```powershell
pip install -r requirements.txt
alembic upgrade head
python -c "from sqlalchemy import text; from app.infrastructure.database.session import engine; print(engine.connect().execute(text(\"SELECT extname FROM pg_extension WHERE extname='vector'\")).all())"
```

The expected table column is `embedding VECTOR(384)`. The readiness endpoint
reports `pgvector: available` only when the PostgreSQL extension is present.

## Local-only vector architecture

EKA uses PostgreSQL plus pgvector rather than ChromaDB or Qdrant. Sentence
Transformers and PyTorch generate the same 384 floating-point values; pgvector
stores those values and performs cosine-distance search. Block 4 can consume
the search endpoint over HTTP without importing Block 3 code.
