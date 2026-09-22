                        ## EKA Learning Platform

                        EKA is a local-first enterprise AI learning platform. The current working
                        services are `document-service`, `ingestion-service`, and `embedding-service`.

                        ## START ALL SERVICES

                        From the EKA root:

                        .\scripts\start-all.ps1

                        Or, when running directly with Python:

                        python scripts/start-all.py

                        Services:

                        Document Service  http://127.0.0.1:8000
                        Ingestion Service http://127.0.0.1:8001
                        Embedding Service http://127.0.0.1:8002

                        Swagger:

                        Document  http://127.0.0.1:8000/docs
                        Ingestion http://127.0.0.1:8001/docs
                        Embedding http://127.0.0.1:8002/docs

                        Individual startup commands:

                        cd services/document-service
                        uvicorn app.main:app --host 127.0.0.1 --port 8000

                        cd services/ingestion-service
                        uvicorn app.main:app --host 127.0.0.1 --port 8001

                        cd services/embedding-service
                        uvicorn app.main:app --host 127.0.0.1 --port 8002

                        Repository architecture and boundaries are documented in:

                        - [Architecture overview](docs/architecture/overview.md)
                        - [Service boundaries](docs/architecture/service-boundaries.md)
                        - [Technology stack](docs/architecture/technology-stack.md)
                        - [Local-only architecture decision](docs/decisions/0001-local-only-architecture.md)

                        EKA-owned contracts and framework-neutral interfaces live under `libraries/`.
                        Third-party frameworks remain dependencies or adapters of the owning service.

                         USER / CLIENT
                              │
                              │
                              │ HTTP POST
                              │ /documents/upload
                              │ multipart/form-data
                              │ file = employee-policy.pdf
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 BLOCK 1 — DOCUMENT SERVICE                  │
│                                                             │
│                    FastAPI Application                      │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. API ROUTE                                          │  │
│  │                                                       │  │
│  │ POST /documents/upload                                │  │
│  │                                                       │  │
│  │ FastAPI receives UploadFile                           │  │
│  └─────────────────────────┬─────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 2. VALIDATION                                         │  │
│  │                                                       │  │
│  │ • File exists                                         │  │
│  │ • File type allowed                                   │  │
│  │ • File size allowed                                   │  │
│  │ • Filename validated                                  │  │
│  └─────────────────────────┬─────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 3. SHA-256 CHECKSUM                                   │  │
│  │                                                       │  │
│  │ File bytes                                             │  │
│  │     ↓                                                 │  │
│  │ hashlib.sha256()                                      │  │
│  │     ↓                                                 │  │
│  │ 64-character checksum                                │  │
│  └─────────────────────────┬─────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 4. DUPLICATE CHECK                                    │  │
│  │                                                       │  │
│  │ SQLAlchemy Repository                                 │  │
│  │          ↓                                            │  │
│  │ PostgreSQL                                             │  │
│  │          ↓                                            │  │
│  │ SELECT ... WHERE checksum = ?                         │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │                                   │
│                  ┌──────┴───────┐                           │
│                  │              │                           │
│              EXISTS         NOT EXISTS                      │
│                  │              │                           │
│                  ▼              ▼                           │
│              HTTP 409       CONTINUE                        │
│                                 │                           │
│                                 ▼                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 5. LOCAL FILE STORAGE                                 │  │
│  │                                                       │  │
│  │ Original PDF/DOCX                                     │  │
│  │          ↓                                            │  │
│  │ StorageService                                        │  │
│  │          ↓                                            │  │
│  │ storage/documents/<document-id>/file.pdf             │  │
│  └─────────────────────────┬─────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 6. DATABASE RECORD                                    │  │
│  │                                                       │  │
│  │ SQLAlchemy ORM                                        │  │
│  │          ↓                                            │  │
│  │ Session.add(document)                                 │  │
│  │          ↓                                            │  │
│  │ session.commit()                                      │  │
│  └─────────────────────────┬─────────────────────────────┘  │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                             ▼
                  ┌───────────────────────┐
                  │    POSTGRESQL 17/18   │
                  │                       │
                  │    documents table    │
                  └───────────────────────┘
                             │
                             ▼
                    API RESPONSE
                             │
                             ▼
                         CLIENT