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