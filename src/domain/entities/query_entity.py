from pydantic import BaseModel, Field
from typing import Optional

class Query(BaseModel):
    """
    Request model for querying the RAG system.
    """

    query: str = Field(..., description="The query string")
    conversation_history: Optional[list[dict[str, str]]] = Field(
        default=None, description="Conversation history for context"
    )
    mode: str = Field(default="naive", description="Query mode: naive, local, global, hybrid")
    stream: bool = Field(default=False, description="Enable streaming response")
    only_need_context: bool = Field(
        default=True, description="Return only chunks, no LLM generation"
    )
    top_k: int = Field(
        default=40, description="Number of entities/relations to retrieve"
    )
    chunk_top_k: int = Field(
        default=20, description="Number of chunks to retrieve"
    )
    enable_rerank: bool = Field(
        default=True, description="Enable reranking of results"
    )
    include_references: bool = Field(
        default=True, description="Include references in response"
    )
    include_metadata: bool = Field(
        default=False, description="Include metadata in response"
    )
