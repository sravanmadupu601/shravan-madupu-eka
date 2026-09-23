# EKA Agent Service (Block 5)

Block 5 is one local FastAPI service that uses LangGraph to route a request to a knowledge lookup, a read-only business-data lookup, both, or a general response. Block 4 owns retrieval and answer generation; Block 5 coordinates tools and validates their results.

## Architecture

```text
POST /agent/query
        |
        v
FastAPI -> AgentService -> LangGraph StateGraph
                              | analyze -> route
                 +------------+-----------+-----------+
                 v                        v           v
          RAG port (Block 4)       local mock data   general
                 |                        |           |
                 +------ validate/rewrite +-----------+
                                   |
                                   v
                    local mock response provider
```

The domain contracts are framework-independent. FastAPI lives in the API layer, LangGraph in `app/agent`, and adapters in `app/tools` and `app/infrastructure`. Tools are intentionally read-only. There is no database, MCP server, shell tool, arbitrary SQL, or cloud dependency.

## LangGraph workflow

The graph is `START -> analyze_request -> route_request`, then routes by intent:

- `KNOWLEDGE` -> `retrieve_knowledge`
- `BUSINESS_DATA` -> `execute_tool`
- `KNOWLEDGE_AND_BUSINESS_DATA` -> retrieval, then business lookup
- `GENERAL` -> `generate_response`

Tool routes pass through `validate_results`. Insufficient knowledge results may pass through `rewrite_query -> retrieve_knowledge`, bounded by `MAX_AGENT_RETRIES` (default 2). Errors stop the retry loop. Every path ends at `generate_response -> END`.

The typed graph state carries the user and normalized queries, intent/route, required tools, rewritten query, retrieved documents, tool results, citations, context, answer, retry limit/count, validation state, safe error codes, warnings, and tools used. It contains no secrets.

Intent analysis is a replaceable deterministic heuristic, not an ML classifier or language model. It recognizes policy/knowledge language and reservation identifiers. The LLM port currently has a deterministic `mock` implementation; it does not call any model or external service.

## Tools and integrations

- **Knowledge:** `RagClient` is the boundary for Block 4. No Block 4 implementation source is present in the workspace. A local service already responding on port 8003 published OpenAPI for `POST /rag/query` (`question` request; `answer`, `citations`, and `retrieved_chunks` response) plus `GET /health/ready`. `HttpRagClient` implements that observed contract. Its source implementation and local-only model/provider behavior cannot be audited from this checkout; the client calls only the configured local URL. Unit tests exercise the mapping with an in-memory HTTP transport, and graph tests inject a fake client.
- **Documents:** `DocumentClient` is an interface with a local unavailable stub. Block 1 currently exposes upload and health only, not document retrieval/search.
- **Business data:** `LocalMockBusinessDataClient` is a read-only demonstration adapter with a single sample reservation (`ABC123`). Its returned data is labeled `LOCAL MOCK DATA`; it is not live enterprise or Marriott data. Replace the adapter behind the port when a real local business API exists.
- **Calculator:** omitted; current intents do not require arithmetic/date calculations.
- **MCP:** not implemented. The ports can later be adapted to Block 6 MCP tools.

Block 5 never imports Block 4 modules or accesses Block 1/Block 4 databases. It has no cross-service database connection.

## API

- `POST /agent/query` — body `{"query":"What is the cancellation policy?"}`. Returns answer, intent, route, citations, tools used, retry count, validation status, and warnings.
- `GET /health` — process liveness.
- `GET /ready` — agent graph readiness and live Block 4 `/health/ready` status; business-only and general requests can still run when RAG is unavailable.
- `GET /info` — safe service and graph-node summary.
- FastAPI schema: `/docs`.

Example combined request: `{"query":"What is the cancellation policy for reservation ABC123?"}`. The local reservation tool can return its sample record; the knowledge lookup calls Block 4 on port 8003. If that service is unavailable, the agent reports the limitation and does not imply that it retrieved policy content.

## Configuration

Copy `.env.example` to `.env` if local overrides are needed. Defaults are local-only:

```dotenv
AGENT_SERVICE_PORT=8004
RAG_SERVICE_URL=http://127.0.0.1:8003
DOCUMENT_SERVICE_URL=http://127.0.0.1:8000
MAX_AGENT_RETRIES=2
LLM_PROVIDER=mock
ENVIRONMENT=development
```

Only `LLM_PROVIDER=mock` is implemented. No API keys are required. The RAG URL is used by the HTTP adapter. The Document URL is retained for a future adapter; Block 1 currently has no document-read/search endpoint.

## Run on Windows

From this directory, create and populate the service's own environment:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8004
```

The root `scripts/start-all.py` includes this service and resolves its own `.venv`. The root launcher currently starts Document (8000), Ingestion (8001), Embedding (8002), and Agent (8004). It does not start RAG on 8003 because no runnable RAG application source is present in the repository, even though a local process currently publishes that API.

## Tests

Run `python -m pytest` from `services/agent-service`. Unit tests inject fake RAG, business-data, and response providers; they do not require PostgreSQL, Block 4, cloud APIs, or external model downloads. They cover intent routes, combined tools, citation propagation, insufficient retrieval and rewrite, retry bounds, tool/provider failures, API validation, health/readiness/info, and bounded graph execution.

The HTTP contract mapping is tested with an in-memory transport. A real Block 4 integration test is not included because the service source is absent and its execution path cannot be verified as local-only from this checkout. Existing Block 1–4 results are reported separately after running their available tests.
