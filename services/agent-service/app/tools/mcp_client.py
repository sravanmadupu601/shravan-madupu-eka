from __future__ import annotations

import asyncio
from urllib.parse import urlsplit, urlunsplit

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from app.domain.models import KnowledgeResult
from app.tools.rag_tool import RagUnavailableError


class StreamableHttpMCPClient:
    """Small synchronous adapter for the official async Streamable HTTP MCP client."""

    def __init__(self, server_url: str, timeout_seconds: float = 10.0):
        self.server_url = server_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def _call_tool(self, name: str, arguments: dict) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as http_client:
            async with streamable_http_client(self.server_url, http_client=http_client) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(name, arguments)
                    if result.isError:
                        raise RagUnavailableError("The local MCP tool returned an error.")
                    structured = result.structuredContent
                    if isinstance(structured, dict):
                        return structured
                    raise RagUnavailableError("The local MCP tool returned no structured result.")

    def call_tool(self, name: str, arguments: dict) -> dict:
        try:
            return asyncio.run(self._call_tool(name, arguments))
        except RagUnavailableError:
            raise
        except Exception as exc:
            raise RagUnavailableError("The local MCP service request failed.") from exc

    def is_ready(self) -> bool:
        parsed = urlsplit(self.server_url)
        health_url = urlunsplit((parsed.scheme, parsed.netloc, "/health", "", ""))
        try:
            response = httpx.get(health_url, timeout=self.timeout_seconds)
            return response.is_success
        except httpx.HTTPError:
            return False


class MCPRagClient:
    """RagClient-compatible adapter that consumes Block 4 through Block 6 MCP."""

    def __init__(self, mcp_client: StreamableHttpMCPClient, top_k: int = 5):
        self.mcp_client = mcp_client
        self.top_k = top_k

    def search_knowledge(self, query: str) -> KnowledgeResult:
        result = self.mcp_client.call_tool(
            "search_knowledge",
            {"query": query, "top_k": self.top_k},
        )
        if result.get("ok") is not True:
            error = result.get("error", {})
            message = error.get("message", "The MCP knowledge tool failed.")
            raise RagUnavailableError(message)
        try:
            return KnowledgeResult.model_validate(result["data"])
        except (KeyError, TypeError, ValueError) as exc:
            raise RagUnavailableError("The MCP knowledge tool returned an invalid response.") from exc

    def is_ready(self) -> bool:
        return self.mcp_client.is_ready()
