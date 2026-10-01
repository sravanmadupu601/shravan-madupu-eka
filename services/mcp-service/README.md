# EKA MCP Service (Block 6)

Block 6 is a local Model Context Protocol adapter. It exposes explicitly allowlisted EKA capabilities as MCP tools, a resource, and a prompt. It is not an Agent or RAG service.

## Architecture

```text
Block 5 Agent / any MCP host
			  |
			  | Streamable HTTP MCP (/mcp)
			  v
	   Block 6 MCP Service
	   | tools / resource / prompt
	   +--------------------+
	   |                    |
	   | HTTP               | HTTP
	   v                    v
Block 4 RAG API       Block 1 Document API
```

Block 5 remains responsible for LangGraph reasoning and routing. Block 6 adapts the standardized MCP protocol to existing HTTP API contracts. It does not access service databases or import Block 1/4 Python modules.

## MCP transport

This service uses the official `mcp` Python SDK 1.26.0 and its FastMCP Streamable HTTP transport. MCP clients connect at `http://127.0.0.1:8005/mcp`. The service also exposes ordinary operational endpoints at `/health`, `/ready`, and `/info`; these are not MCP protocol endpoints.

## Tools

- `search_knowledge(query, top_k)`: calls Block 4 `POST /rag/query`, returns its answer and preserves its citations. It does not embed queries or perform retrieval itself.
- `get_document(document_id)`: calls Block 1 `GET /documents/{document_id}` and returns safe metadata, not file contents or storage paths.
- `list_documents(limit, offset)`: calls Block 1 `GET /documents` with pagination.
- `document_health()`: checks Block 1 `GET /health/ready`.
- `rag_health()`: checks Block 4 `GET /health/ready`.

Errors are returned as structured `{ok: false, error: {code, message}}` tool results. Downstream failures, timeouts, 404s, and malformed responses are normalized without returning stack traces or connection details.

## Resource

`eka://documents` returns a JSON page of safe document metadata using Block 1's document list API. It never reads document files or accesses the Block 1 database.

## Prompt

`enterprise_knowledge_query(query, response_style, citation_required)` creates a grounded prompt that tells the model to use retrieved EKA knowledge, preserve citations, state when information is unavailable, and avoid fabricated facts. `citation_required` is the MCP prompt argument string `required` or `optional`, as required by MCP prompt argument schemas. The MCP service does not call or select an LLM.

## Block 1 compatibility addition

Block 1 previously exposed upload and health but no metadata read/list operations. Two additive read-only API routes were added for this adapter:

- `GET /documents/{document_id}`
- `GET /documents?limit=50&offset=0`

They return the existing metadata schema and never reveal `storage_path`.

## Configuration

Copy `.env.example` to `.env` if overrides are needed. Defaults bind only to loopback:

```dotenv
MCP_SERVICE_HOST=127.0.0.1
MCP_SERVICE_PORT=8005
RAG_SERVICE_URL=http://127.0.0.1:8003
DOCUMENT_SERVICE_URL=http://127.0.0.1:8000
REQUEST_TIMEOUT_SECONDS=10
```

Configuration validation rejects non-loopback integration URLs and embedded credentials. There is no cloud authentication, external identity provider, filesystem tool, shell tool, or database administration tool.

## Run on Windows

```powershell
cd services/mcp-service
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8005
```

Run tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The root `scripts/start-all.py` and `scripts/start-all.ps1` register MCP on port 8005.

## Example MCP client

Using the official SDK client:

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
	async with streamable_http_client("http://127.0.0.1:8005/mcp") as (read, write, _):
		async with ClientSession(read, write) as session:
			await session.initialize()
			tools = await session.list_tools()
			result = await session.call_tool(
				"search_knowledge",
				{"query": "What is the cancellation policy?", "top_k": 5},
			)
			print([tool.name for tool in tools.tools])
			print(result.structuredContent)

asyncio.run(main())
```

## Block 5 integration

The service is available to Block 5 or another MCP host at the local Streamable HTTP endpoint. Block 5 now has a small MCP-backed `RagClient` adapter that invokes `search_knowledge`; its LangGraph, business-data routing, and reasoning remain in Block 5. The former direct HTTP RAG adapter remains available for compatibility but is not the default.
