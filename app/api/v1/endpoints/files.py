from fastapi import APIRouter, Depends
from app.models.schemas import FileListResponse, DeleteResponse
from app.services.file_service import FileService
from app.dependencies import get_file_service

router = APIRouter()

@router.get("/", response_model=FileListResponse)
async def list_files(
    file_service: FileService = Depends(get_file_service)
):
    """List all uploaded files."""
    return await file_service.list_files()

@router.delete("/{filename}", response_model=DeleteResponse)
async def delete_file(
    filename: str,
    file_service: FileService = Depends(get_file_service)
):
    """Delete a file and its associated vectors."""
    return await file_service.delete_file(filename)
