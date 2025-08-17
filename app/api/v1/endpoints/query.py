from fastapi import APIRouter, Depends
from app.models.schemas import QueryRequest, QueryResponse
from app.services.query_service import QueryService
from app.dependencies import get_query_service

router = APIRouter()

@router.post("/", response_model=QueryResponse)
def query_documents(
    req: QueryRequest,
    query_service: QueryService = Depends(get_query_service)
):
    """Query documents using RAG."""
    return query_service.process_query(req)
