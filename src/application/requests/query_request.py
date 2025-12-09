from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """
    Request model for querying the RAG system.
    """

    query: str = Field(..., description="The query string")
    mode: str = Field(default="naive", description="Query mode: naive, local, global, hybrid")
    stream: bool = Field(default=False, description="Enable streaming response")
    
    only_need_context: bool = Field(
        default=True, description="Return only chunks, no LLM generation"
    )
    only_need_prompt: bool = Field(
        default=False, description="Return only the constructed prompt"
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
