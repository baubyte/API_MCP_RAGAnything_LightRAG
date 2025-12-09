"""
MCP tools for RAGAnything.
These tools are registered with FastMCP for Claude Desktop integration.
"""
from dependencies import get_query_use_case
from application.requests.query_request import QueryRequest
from fastmcp import FastMCP
import json


# MCP instance will be configured in dependencies.py
mcp = FastMCP("RAGAnything")


@mcp.tool()
async def query_knowledge_base(query: str, mode: str = "naive", chunk_top_k: int = 10) -> str:
    """
    Query the RAGAnything knowledge base and retrieve relevant document chunks.
    begin by using naive way, in case no results ask the user if he wants to try a wider search.
    for this use hybrid and increase chunk_top_k to 20
    
    Args:
        query: The question or query to search for in the knowledge base
        mode: The query mode (naive, local, global, hybrid)
    
    Returns:
        str: JSON string containing relevant chunks from the knowledge base
    """
    try:
        use_case = await get_query_use_case()
        request = QueryRequest(
            query=query,
            mode=mode,
            only_need_context=True,
            chunk_top_k=chunk_top_k,
            include_references=True,
            enable_rerank=False
        )
        
        result = await use_case.execute(request)
        
        if not result.chunks:
            return "No relevant chunks found for your query."
        
        return json.dumps({
            "chunks": result.chunks,
            "count": len(result.chunks)
        }, indent=2)
        
    except Exception as e:
        return f"Error querying knowledge base: {str(e)}"
