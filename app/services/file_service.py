import os
from typing import List
from app.core.config import settings
from app.models.schemas import FileListResponse, DeleteResponse
from app.models.mongo_models import DocumentCollection, VectorMetadata
from app.services.embedding_service import EmbeddingService

# class FileService:
#     """Service for managing files and their associated data."""
    
#     def __init__(self, embedding_service: EmbeddingService):
#         self.embedding_service = embedding_service
    
#     async def list_files(self) -> FileListResponse:
#         """List all uploaded files with MongoDB metadata."""
#         try:
#             # Get all document collections from MongoDB
#             documents = await DocumentCollection.find_all().to_list()
            
#             file_list = []
#             for doc in documents:
#                 file_info = {
#                     "filename": doc.filename,
#                     "file_type": doc.file_type,
#                     "file_size": doc.file_size,
#                     "status": doc.status,
#                     "total_chunks": doc.total_chunks,
#                     "uploaded_at": doc.uploaded_at.isoformat(),
#                     "processed_at": doc.processed_at.isoformat() if doc.processed_at else None,
#                     "total_pages": doc.total_pages,
#                     "total_slides": doc.total_slides,
#                     "sheet_names": doc.sheet_names
#                 }
#                 file_list.append(file_info)
            
#             return FileListResponse(files=file_list)
#         except Exception as e:
#             return FileListResponse(files=[])
    



class FileService:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
    
    async def list_files(self) -> FileListResponse:
        """List all uploaded files with MongoDB metadata."""
        try:
            print(f"🔍 Querying MongoDB database: {settings.DATABASE_NAME}")
            print(f"🔍 Collection: document_collections")
            
            # Test the connection first
            documents = await DocumentCollection.find_all().to_list()
            print(f"📊 Found {len(documents)} documents in MongoDB")
            
            if not documents:
                print("⚠️ No documents found in MongoDB, falling back to file system")
                # Fallback to file system
                files = []
                if os.path.exists(settings.UPLOAD_DIR):
                    for filename in os.listdir(settings.UPLOAD_DIR):
                        if os.path.isfile(os.path.join(settings.UPLOAD_DIR, filename)):
                            files.append(filename)
                return FileListResponse(files=files)
            
            file_list = []
            for doc in documents:
                print(f"📄 Processing document: {doc.filename}")
                file_info = doc.filename
                file_list.append(file_info)
            
            return FileListResponse(files=file_list)
            
        except Exception as e:
            print(f"❌ Error in list_files: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to file system approach
            files = []
            if os.path.exists(settings.UPLOAD_DIR):
                for filename in os.listdir(settings.UPLOAD_DIR):
                    if os.path.isfile(os.path.join(settings.UPLOAD_DIR, filename)):
                        files.append(filename)
            return FileListResponse(files=files)
    async def delete_file(self, filename: str) -> DeleteResponse:
        """Delete file and all associated data from MongoDB and Pinecone."""
        try:
            # Find document collection
            doc_collection = await DocumentCollection.find_one(
                DocumentCollection.filename == filename
            )
            
            if not doc_collection:
                return DeleteResponse(
                    status="error",
                    message=f"File {filename} not found in database"
                )
            
            # Get all vector metadata for this document
            vector_metadata = await VectorMetadata.find(
                VectorMetadata.document_filename == filename
            ).to_list()
            
            if vector_metadata:
                # Get vector IDs for Pinecone deletion
                vector_ids = [meta.vector_id for meta in vector_metadata]
                
                # Delete vectors from Pinecone
                self.embedding_service.delete_vectors(vector_ids)
                
                # Delete vector metadata from MongoDB
                await VectorMetadata.find(
                    VectorMetadata.document_filename == filename
                ).delete()
            
            # Delete document collection record
            await doc_collection.delete()
            
            # Delete physical file
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return DeleteResponse(
                status="success",
                message=f"File {filename} and {len(vector_metadata)} associated vectors deleted successfully"
            )
            
        except Exception as e:
            return DeleteResponse(
                status="error",
                message=f"Error deleting file: {str(e)}"
            )    