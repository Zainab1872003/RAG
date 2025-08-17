import os
import shutil
from datetime import datetime
from fastapi import UploadFile, HTTPException
from docx2pdf import convert
from app.core.config import settings
from app.models.mongo_models import DocumentCollection, VectorMetadata
from app.services.embedding_service import EmbeddingService
from app.utils.doc_loader import load_and_chunk_pdf, load_and_chunk_excel, load_and_chunk_ppt
from app.utils.ppt_converter import ppt_to_pptx_soffice

class DocumentService:
    """Service for processing and managing documents."""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
    
    async def process_upload(self, file: UploadFile):
        """Process uploaded file and create embeddings with MongoDB tracking."""
        save_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        print(f"Processing upload: {save_path}")
        
        # Create document collection record
        doc_collection = DocumentCollection(
            filename=file.filename,
            original_filename=file.filename,
            file_type=os.path.splitext(file.filename)[1].lower(),
            file_size=0,  # Will update after saving
            chunk_size=settings.PDF_CHUNK_SIZE,
            overlap=settings.PDF_CHUNK_OVERLAP,
            status="processing"
        )
        await doc_collection.create()
        
        try:
            # Save file to disk
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Update file size
            doc_collection.file_size = os.path.getsize(save_path)
            await doc_collection.save()
            
            ext = os.path.splitext(save_path)[1].lower()
            flag = 0
            
            # Handle file conversions
            if ext == ".ppt":
                try:
                    save_path = ppt_to_pptx_soffice(save_path)
                    ext = ".pptx"
                    os.remove(os.path.splitext(save_path)[0] + ".ppt")
                except Exception as e:
                    doc_collection.status = "failed"
                    doc_collection.error_message = f"PPT conversion failed: {e}"
                    await doc_collection.save()
                    raise HTTPException(status_code=422, detail=f"PPT conversion failed: {e}")
            
            if ext in ['.doc', '.docx']:
                convert(save_path, settings.UPLOAD_DIR)
                pdf_path = os.path.splitext(save_path)[0] + ".pdf"
                flag = 1
            else:
                pdf_path = save_path
            
            # Process based on file type and get chunks + metadata
            if ext in ['.xlsx', '.xls']:
                chunks, metadata = load_and_chunk_excel(save_path)
                # Get sheet names for MongoDB
                import pandas as pd
                with pd.ExcelFile(save_path) as xls:
                    doc_collection.sheet_names = list(xls.sheet_names)
            elif ext == '.pptx':
                chunks, metadata = load_and_chunk_ppt(save_path)
                # Count slides
                from pptx import Presentation
                prs = Presentation(save_path)
                doc_collection.total_slides = len(prs.slides)
            else:
                chunks, metadata = load_and_chunk_pdf(pdf_path)
                # Count pages
                import fitz
                doc = fitz.open(pdf_path)
                doc_collection.total_pages = len(doc)
                doc.close()
            
            if not chunks:
                doc_collection.status = "failed"
                doc_collection.error_message = "No content could be extracted"
                await doc_collection.save()
                raise HTTPException(status_code=422, detail="No content could be extracted from the file")
            
            # Update document collection with chunk count
            doc_collection.total_chunks = len(chunks)
            await doc_collection.save()
            
            # Create vector metadata records (WITHOUT storing text)
            vector_metadata_list = []
            for i, meta in enumerate(metadata):
                vector_id = f"{file.filename}_{i}"
                
                vector_meta = VectorMetadata(
                    vector_id=vector_id,
                    document_filename=file.filename,
                    chunk_index=i,
                    page=meta.get('page'),
                    slide=meta.get('slide'),
                    sheet=meta.get('sheet'),
                    start_row=meta.get('start_row'),
                    end_row=meta.get('end_row'),
                    chunk_length=len(meta.get('text', '')),
                    has_images=meta.get('has_images', False),
                    image_count=meta.get('image_count', 0),
                    embedding_model=settings.EMBEDDING_MODEL
                )
                vector_metadata_list.append(vector_meta)
            
            # Bulk insert vector metadata
            await VectorMetadata.insert_many(vector_metadata_list)
            
            # Create embeddings and store in Pinecone (text not stored in MongoDB)
            self.embedding_service.embed_and_upsert(chunks, metadata)
            
            # Mark as completed
            doc_collection.status = "completed"
            doc_collection.processed_at = datetime.utcnow()
            await doc_collection.save()
            
            # Cleanup temporary files
            if flag:
                os.remove(save_path)
            
            return {
                "message": f"{file.filename} uploaded and processed successfully!",
                "filename": file.filename,
                "chunks_created": len(chunks),
                "document_id": str(doc_collection.id)
            }
            
        except Exception as e:
            # Update error status
            doc_collection.status = "failed"
            doc_collection.error_message = str(e)
            await doc_collection.save()
            
            # Cleanup on error
            if os.path.exists(save_path):
                os.remove(save_path)
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
