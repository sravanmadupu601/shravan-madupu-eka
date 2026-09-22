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

Vectors are intentionally not returned by the API. They are stored as JSON in
the first PostgreSQL implementation so a future vector-store repository can be
introduced without changing the application/domain layers.

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

## Future vector-store migration

The repository contract is intentionally independent of storage technology.
Future `PgVector`, Qdrant, or Chroma adapters can replace the PostgreSQL JSON
adapter without changing the application service or provider interface.
