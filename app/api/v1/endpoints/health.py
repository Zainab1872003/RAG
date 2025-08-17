from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def health_check():
    """Detailed health check with configuration info"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "api_version": "v1"
    }

@router.get("/info")
def get_info():
    """Get system configuration info"""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "upload_dir": settings.UPLOAD_DIR,
        "max_file_size_mb": settings.MAX_FILE_SIZE // (1024 * 1024),
        "embedding_model": settings.EMBEDDING_MODEL,
        "mistral_url": settings.MISTRAL_BASE_URL,
        "pinecone_index": settings.PINECONE_INDEX_NAME
    }
