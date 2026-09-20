# EKA Ingestion Service

Block 2 owns document processing: parsing, deterministic text cleaning, chunking, and processed-chunk persistence.

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
