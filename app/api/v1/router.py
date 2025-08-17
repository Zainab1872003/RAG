from fastapi import APIRouter
from app.api.v1.endpoints import health, upload, query, files

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
