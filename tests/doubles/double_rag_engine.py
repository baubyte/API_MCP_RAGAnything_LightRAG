from typing import Optional, List
from dataclasses import dataclass, field

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from domain.ports.rag_engine import RAGEnginePort
from domain.entities.indexing_result import (
    FileIndexingResult,
    FolderIndexingResult,
    IndexingStatus,
    FolderIndexingStats,
)


@dataclass
class IndexDocumentCall:
    """Record of a call to index_document."""

    file_path: str
    file_name: str
    output_dir: str


@dataclass
class IndexFolderCall:
    """Record of a call to index_folder."""

    folder_path: str
    output_dir: str
    recursive: bool
    file_extensions: Optional[List[str]]


class DoubleRAGEngine(RAGEnginePort):
    """
    Test double for RAGEnginePort.
    Returns configurable responses and tracks calls for assertions.
    """

    def __init__(self) -> None:
        self.index_document_calls: list[IndexDocumentCall] = []
        self.index_folder_calls: list[IndexFolderCall] = []

        self._index_document_result: Optional[FileIndexingResult] = None
        self._index_folder_result: Optional[FolderIndexingResult] = None

    def set_index_document_result(self, result: FileIndexingResult) -> None:
        """Configure the result to return from index_document."""
        self._index_document_result = result

    def set_index_folder_result(self, result: FolderIndexingResult) -> None:
        """Configure the result to return from index_folder."""
        self._index_folder_result = result

    async def index_document(
        self, file_path: str, file_name: str, output_dir: str
    ) -> FileIndexingResult:
        """
        Record the call and return configured result.

        Args:
            file_path: Absolute path to the document to index.
            file_name: Name of the file being indexed.
            output_dir: Directory for processing outputs.

        Returns:
            FileIndexingResult: Configured result or default success.
        """
        self.index_document_calls.append(
            IndexDocumentCall(
                file_path=file_path,
                file_name=file_name,
                output_dir=output_dir,
            )
        )

        if self._index_document_result is not None:
            return self._index_document_result

        return FileIndexingResult(
            status=IndexingStatus.SUCCESS,
            message="Document indexed successfully",
            file_path=file_path,
            file_name=file_name,
            processing_time_ms=100.0,
        )

    async def index_folder(
        self,
        folder_path: str,
        output_dir: str,
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None,
    ) -> FolderIndexingResult:
        """
        Record the call and return configured result.

        Args:
            folder_path: Absolute path to the folder containing documents.
            output_dir: Directory for processing outputs.
            recursive: Whether to process subdirectories recursively.
            file_extensions: Optional list of file extensions to filter.

        Returns:
            FolderIndexingResult: Configured result or default success.
        """
        self.index_folder_calls.append(
            IndexFolderCall(
                folder_path=folder_path,
                output_dir=output_dir,
                recursive=recursive,
                file_extensions=file_extensions,
            )
        )

        if self._index_folder_result is not None:
            return self._index_folder_result

        return FolderIndexingResult(
            status=IndexingStatus.SUCCESS,
            message="Folder indexed successfully",
            folder_path=folder_path,
            recursive=recursive,
            stats=FolderIndexingStats(
                total_files=5,
                files_processed=5,
                files_failed=0,
                files_skipped=0,
            ),
            processing_time_ms=500.0,
        )

    async def initialize(self) -> bool:
        """No-op initialization for tests."""
        return True
