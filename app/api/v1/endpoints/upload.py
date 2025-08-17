# app/api/v1/endpoints/upload.py
from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from app.models.schemas import UploadResponse
from app.services.document_service import DocumentService
from app.dependencies import get_document_service

router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    doc_service: DocumentService = Depends(get_document_service)
):
    """Upload and process a document file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file extension
    allowed_extensions = {'.pdf', '.doc', '.docx', '.xlsx', '.xls', '.pptx', '.ppt'}
    file_ext = f".{file.filename.lower().split('.')[-1]}"
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        result = await doc_service.process_upload(file)
        return UploadResponse(
            message=result["message"],
            filename=result["filename"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

