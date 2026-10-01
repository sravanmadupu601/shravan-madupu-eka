# ADR 0001: Local-Only Architecture

- Status: accepted
- Date: 2026-09-21

## Decision

EKA is a local-first enterprise AI learning platform. PostgreSQL is the primary relational database, and the local filesystem is the document storage mechanism.

Third-party AI frameworks and infrastructure may be evaluated locally, but cloud providers, cloud storage, cloud deployment, and Databricks are out of scope.

## Consequences

Each service must use configuration for local endpoints and paths, avoid credentials in source control, and keep its own database migrations independent. Future integrations must sit behind EKA-owned interfaces where practical.
