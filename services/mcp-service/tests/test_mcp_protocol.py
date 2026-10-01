import asyncio

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from pydantic import AnyUrl

from app.application.service import MCPApplicationService
from app.infrastructure.mcp.server import create_mcp_server
from tests.conftest import FakeDocumentClient, FakeRagClient


def test_official_mcp_client_discovers_tools_resource_prompt_and_calls_tool():
    async def run_protocol_check():
        service = MCPApplicationService(FakeRagClient(), FakeDocumentClient())
        server = create_mcp_server(service, "EKA MCP Test", "127.0.0.1", 8005)
        app = server.streamable_http_app()
        async with server.session_manager.run():
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://127.0.0.1",
            ) as http_client:
                async with streamable_http_client(
                    "http://127.0.0.1/mcp",
                    http_client=http_client,
                ) as (read_stream, write_stream, _):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        tools = await session.list_tools()
                        resources = await session.list_resources()
                        prompts = await session.list_prompts()
                        called = await session.call_tool("document_health", {})
                        search = await session.call_tool(
                            "search_knowledge",
                            {"query": "policy question", "top_k": 3},
                        )
                        resource_content = await session.read_resource(AnyUrl("eka://documents"))
                        prompt = await session.get_prompt(
                            "enterprise_knowledge_query",
                            arguments={"query": "policy question", "citation_required": "required"},
                        )

        assert {item.name for item in tools.tools} == {
            "search_knowledge",
            "get_document",
            "list_documents",
            "document_health",
            "rag_health",
        }
        assert [str(item.uri) for item in resources.resources] == ["eka://documents"]
        assert [item.name for item in prompts.prompts] == ["enterprise_knowledge_query"]
        assert called.isError is False
        assert search.structuredContent["data"]["answer"] == "Policy result"
        assert "documents" in resource_content.contents[0].text
        assert "never invent citations" in prompt.messages[0].content.text

    asyncio.run(run_protocol_check())
