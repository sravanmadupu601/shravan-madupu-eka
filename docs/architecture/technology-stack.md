# Technology Stack

| Area | Technology or boundary |
| --- | --- |
| Core language | Python |
| APIs | FastAPI and Uvicorn |
| Validation and contracts | Pydantic |
| Relational persistence | PostgreSQL, SQLAlchemy, Psycopg |
| Migrations | Alembic, independently owned per service |
| Document parsing | pypdf and python-docx in ingestion-service |
| Data analysis | Pandas, NumPy, Matplotlib, and Plotly when implemented |
| Traditional ML | scikit-learn |
| Deep learning | PyTorch and TensorFlow experiments |
| AI application components | LangChain and LlamaIndex as future local dependencies |
| Agent orchestration | LangGraph as a future local dependency |
| Tool integration | MCP as a future local service dependency |
| Observability | EKA interfaces first; OpenTelemetry integration later |
| Runtime | Local filesystem, PostgreSQL, and Docker |
| CI | GitHub Actions |

Frameworks are dependencies or adapters, not EKA-owned microservices. Model-specific dependencies stay isolated to the service or experiment that needs them.
