from app.services.embedding_service import EmbeddingService
from app.services.document_service import DocumentService
from app.services.query_service import QueryService
from app.services.file_service import FileService
from app.core.config import settings

# Singleton instances
_embedding_service = None
_document_service = None
_query_service = None
_file_service = None

def get_settings():
    """Get application settings."""
    return settings

def get_embedding_service() -> EmbeddingService:
    """Get singleton embedding service."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

def get_document_service() -> DocumentService:
    """Get singleton document service."""
    global _document_service
    if _document_service is None:
        embedding_service = get_embedding_service()
        _document_service = DocumentService(embedding_service)
    return _document_service

def get_query_service() -> QueryService:
    """Get singleton query service."""
    global _query_service
    if _query_service is None:
        embedding_service = get_embedding_service()
        _query_service = QueryService(embedding_service)
    return _query_service

def get_file_service() -> FileService:
    """Get singleton file service."""
    global _file_service
    if _file_service is None:
        embedding_service = get_embedding_service()
        _file_service = FileService(embedding_service)
    return _file_service

