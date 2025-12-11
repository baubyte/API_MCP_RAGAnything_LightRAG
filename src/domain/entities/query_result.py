from pydantic import BaseModel, Field
from typing import Optional, List


class EntityResult(BaseModel):
    """Represents an entity from the knowledge graph."""

    entity_name: str = Field(description="Entity identifier")
    entity_type: str = Field(description="Entity category/type")
    description: str = Field(description="Entity description")
    source_id: str = Field(description="Source chunk references")
    file_path: str = Field(description="Origin file path")
    created_at: int = Field(description="Creation timestamp")
    reference_id: Optional[dict] = Field(
        default=None, description="Reference identifier for citations"
    )


class RelationshipResult(BaseModel):
    """Represents a relationship from the knowledge graph."""

    src_id: str = Field(description="Source entity name")
    tgt_id: str = Field(description="Target entity name")
    description: str = Field(description="Relationship description")
    keywords: str = Field(description="Relationship keywords")
    weight: float = Field(description="Relationship strength")
    source_id: str = Field(description="Source chunk references")
    file_path: str = Field(description="Origin file path")
    created_at: int = Field(description="Creation timestamp")
    reference_id: Optional[dict] = Field(
        default=None, description="Reference identifier for citations"
    )


class ChunkResult(BaseModel):
    """Represents a document chunk."""

    content: str = Field(description="Document chunk content")
    file_path: str = Field(description="Origin file path")
    chunk_id: str = Field(description="Unique chunk identifier")
    reference_id: str = Field(description="Reference identifier for citations")


class ReferenceResult(BaseModel):
    """Represents a reference mapping."""

    reference_id: str = Field(description="Reference identifier")
    file_path: str = Field(description="Corresponding file path")


class QueryData(BaseModel):
    """Contains the main query result data."""

    entities: List[EntityResult] = Field(default_factory=list)
    relationships: List[RelationshipResult] = Field(default_factory=list)
    chunks: List[ChunkResult] = Field(default_factory=list)
    references: List[ReferenceResult] = Field(default_factory=list)


class KeywordsInfo(BaseModel):
    """Keywords extracted from the query."""

    high_level: List[str] = Field(
        default_factory=list, description="High-level keywords extracted"
    )
    low_level: List[str] = Field(
        default_factory=list, description="Low-level keywords extracted"
    )


class ProcessingInfo(BaseModel):
    """Processing statistics for the query."""

    total_entities_found: int = Field(
        default=0, description="Total entities before truncation"
    )
    total_relations_found: int = Field(
        default=0, description="Total relations before truncation"
    )
    entities_after_truncation: int = Field(
        default=0, description="Entities after token truncation"
    )
    relations_after_truncation: int = Field(
        default=0, description="Relations after token truncation"
    )
    merged_chunks_count: int = Field(
        default=0, description="Chunks before final processing"
    )
    final_chunks_count: int = Field(default=0, description="Final chunks in result")


class QueryMetadata(BaseModel):
    """Metadata about the query execution."""

    query_mode: str = Field(description="Query mode used")
    keywords: Optional[KeywordsInfo] = Field(default=None)
    processing_info: Optional[ProcessingInfo] = Field(default=None)


class QueryResult(BaseModel):
    """Represents the result of a RAG query."""

    status: str = Field(description="Query status ('success' or 'error')")
    message: str = Field(description="Status message")
    answer: Optional[str] = Field(default=None, description="LLM generated answer")
    data: Optional[QueryData] = Field(default=None, description="Query result data")
    metadata: Optional[QueryMetadata] = Field(
        default=None, description="Query metadata"
    )
