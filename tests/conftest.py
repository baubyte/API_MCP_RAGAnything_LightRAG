import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from tests.doubles.double_rag_engine import DoubleRAGEngine
from domain.entities.indexing_result import (
    FileIndexingResult,
    FolderIndexingResult,
    IndexingStatus,
    FolderIndexingStats,
)


@pytest.fixture
def double_rag_engine() -> DoubleRAGEngine:
    """Provide a fresh DoubleRAGEngine instance."""
    return DoubleRAGEngine()


@pytest.fixture
def sample_file_indexing_result() -> FileIndexingResult:
    """Provide a sample successful file indexing result."""
    return FileIndexingResult(
        status=IndexingStatus.SUCCESS,
        message="Document indexed successfully",
        file_path="/tmp/test/document.pdf",
        file_name="document.pdf",
        processing_time_ms=150.0,
    )


@pytest.fixture
def sample_folder_indexing_result() -> FolderIndexingResult:
    """Provide a sample successful folder indexing result."""
    return FolderIndexingResult(
        status=IndexingStatus.SUCCESS,
        message="Folder indexed successfully",
        folder_path="/tmp/test/documents",
        recursive=True,
        stats=FolderIndexingStats(
            total_files=10,
            files_processed=8,
            files_failed=1,
            files_skipped=1,
        ),
        processing_time_ms=1200.0,
    )
