# EKA Ingestion Service

Block 2 owns document processing: parsing, deterministic text cleaning, chunking, and processed-chunk persistence.

## Chunking strategies

The service supports two selectable strategies:

- `fixed` (default): the existing character-size chunker using `CHUNK_SIZE` and `CHUNK_OVERLAP`.
- `semantic`: sentence-aware chunks based on local Sentence Transformer embeddings and cosine similarity.

Semantic chunking uses `sentence-transformers/all-MiniLM-L6-v2` through PyTorch on CPU by default. The model is loaded lazily once per process and cached by the local Hugging Face model cache. No API key or hosted inference service is required.

Set these values in the service `.env` to select semantic chunking:

```dotenv
CHUNKING_STRATEGY=semantic
SEMANTIC_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
SEMANTIC_SIMILARITY_THRESHOLD=0.70
SEMANTIC_MIN_SENTENCES=1
SEMANTIC_MAX_SENTENCES=20
EMBEDDING_DEVICE=cpu
```

Return to fixed-size chunking with `CHUNKING_STRATEGY=fixed`. Change `PROCESSING_VERSION` when changing processing behavior so completed documents are reprocessed.

## Local storage contract

Block 1 stores originals in the configured `DOCUMENT_STORAGE_PATH`. Block 2 resolves a document ID using one of these local-only layouts:

- `<DOCUMENT_STORAGE_PATH>/<document_id>.<extension>`
- `<DOCUMENT_STORAGE_PATH>/<document_id>/file.<extension>`

The service reads originals and never copies or modifies them.

## Idempotency

An ingestion run is unique by `document_id` and `PROCESSING_VERSION`. A completed run is returned on repeat requests. Failed runs are retried and their prior chunks are replaced transactionally.

## Run locally

```powershell
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --port 8001
python -m pytest -v
```
