from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from domain.entities.query_result import QueryResult
from domain.entities.query_entity import Query
from domain.entities.indexing_result import FileIndexingResult, FolderIndexingResult


class RAGEnginePort(ABC):
    """
    Port interface for RAG engine operations.
    Defines the contract for RAG indexing and querying functionality.
    """

    @abstractmethod
    async def index_document(
        self, file_path: str, file_name: str, output_dir: str
    ) -> FileIndexingResult:
        """
        Index a single document into the RAG system.

        Args:
            file_path: Absolute path to the document to index.
            file_name: Name of the file being indexed.
            output_dir: Directory for processing outputs.

        Returns:
            FileIndexingResult: Structured result of the indexing operation.
        """
        pass

    @abstractmethod
    async def index_folder(
        self,
        folder_path: str,
        output_dir: str,
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None,
    ) -> FolderIndexingResult:
        """
        Index all documents in a folder.

        Args:
            folder_path: Absolute path to the folder containing documents.
            output_dir: Directory for processing outputs.
            recursive: Whether to process subdirectories recursively.
            file_extensions: Optional list of file extensions to filter.

        Returns:
            FolderIndexingResult: Structured result with statistics and file details.
        """
        pass

    @abstractmethod
    async def query(self, query: Query) -> QueryResult:
        """
        Query the RAG system.

        Args:
            query: The query string.
            mode: Query mode (naive, local, global, hybrid).
            only_need_context: Return only context without LLM generation.
            **kwargs: Additional query parameters.

        Returns:
            QueryResult: The structured query result.
        """
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the RAG engine.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        pass
