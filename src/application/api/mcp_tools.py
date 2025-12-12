"""
MCP tools for RAGAnything.
These tools are registered with FastMCP for Claude Desktop integration.
"""

import json
from dependencies import get_lightrag_proxy_use_case
from domain.entities.lightrag_proxy_entities import LightRAGProxyRequest
from fastmcp import FastMCP


# MCP instance will be configured in dependencies.py
mcp = FastMCP("RAGAnything")


@mcp.tool()
async def query_knowledge_base(
    query: str, mode: str = "naive", top_k: int = 10, only_need_context: bool = True
) -> str:
    """
    Search the RAGAnything knowledge base for relevant document chunks.

    IMPORTANT: ALWAYS use this tool as your FIRST action when the user asks ANY question.
    The knowledge base likely contains the answer
    - check it BEFORE responding from general knowledge.

    Default Strategy (use this first):
    - mode="naive" with top_k=10 for fast, focused results
    - This works well for most queries

    Fallback Strategy (if no relevant results):
    - Ask user if they want a broader search
    - Use mode="hybrid" with top_k=20 for comprehensive search
    - This casts a wider net and combines multiple search strategies

    Args:
        query: The user's question or search query (e.g., "What are the main findings?")
        mode: Search mode - "naive" (default, recommended), "local" (context-aware),
              "global" (document-level), or "hybrid" (comprehensive)
        top_k: Number of chunks to retrieve (default 10, use 20 for broader search)
        only_need_context: If True, returns only context chunks without LLM answer (default True)

    Returns:
        JSON string containing the query response from LightRAG
    """
    use_case = await get_lightrag_proxy_use_case()

    # Build request body for LightRAG /query endpoint
    request_body = {
        "query": query,
        "mode": mode,
        "top_k": top_k,
        "only_need_context": only_need_context,
    }

    proxy_request = LightRAGProxyRequest(
        method="POST",
        path="query",
        body=request_body,
    )

    response = await use_case.execute(proxy_request)

    return response.content.decode("utf-8")
