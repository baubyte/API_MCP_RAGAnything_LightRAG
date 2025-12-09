from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from application.use_cases.index_file_use_case import IndexFileUseCase
from application.use_cases.index_folder_use_case import IndexFolderUseCase
from application.requests.indexing_request import IndexFolderRequest
from dependencies import get_index_file_use_case, get_index_folder_use_case
from fastapi import status
import os
import shutil
import tempfile


indexing_router = APIRouter(tags=["Indexing"])


@indexing_router.post("/index", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def index_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    use_case: IndexFileUseCase = Depends(get_index_file_use_case),
):
    """
    Index a single file upload in the background.

    Args:
        background_tasks: FastAPI background tasks handler.
        file: The uploaded file to index.
        use_case: The indexing use case dependency.

    Returns:
        dict: Status message indicating indexing started.
    """
    output_dir = os.path.join(tempfile.gettempdir(), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, file.filename or "upload")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    background_tasks.add_task(
        use_case.execute,
        file_path=file_path,
        filename=file.filename or "upload",
        output_dir=output_dir
    )
    
    return {"status": "accepted", "message": "File indexing started in background"}


@indexing_router.post(
    "/index-folder", response_model=dict, status_code=status.HTTP_202_ACCEPTED
)
async def index_folder(
    request: IndexFolderRequest,
    background_tasks: BackgroundTasks,
    use_case: IndexFolderUseCase = Depends(get_index_folder_use_case),
):
    """
    Index all documents in a folder in the background.

    Args:
        request: The indexing request containing folder path and parameters.
        background_tasks: FastAPI background tasks handler.
        use_case: The indexing use case dependency.

    Returns:
        dict: Status message indicating indexing started.
    """
    output_dir = os.path.join(tempfile.gettempdir(), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    background_tasks.add_task(
        use_case.execute,
        request=request,
        output_dir=output_dir
    )
    
    return {"status": "accepted", "message": "Folder indexing started in background"}

