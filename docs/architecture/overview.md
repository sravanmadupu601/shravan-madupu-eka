# EKA Architecture Overview

EKA is a local-first enterprise AI learning platform.

## Current services

- `services/document-service`: owns document upload, validation, original local storage, metadata, checksum, duplicate detection, and document lifecycle.
- `services/ingestion-service`: owns parsing, extraction, normalization, chunking, processed-chunk persistence, ingestion status, and idempotency.

## Planned services

Embedding, RAG, agent, MCP, ML, data analysis, and evaluation services have reserved structure only. They are not implemented by this scaffold.

## Boundaries

Services are business capabilities. Libraries contain small EKA-owned abstractions. Third-party frameworks remain dependencies/adapters. Infrastructure contains local runtime configuration.

All persistence and model execution remain local. No cloud deployment or cloud storage is part of the architecture.
