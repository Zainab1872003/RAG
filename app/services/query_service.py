from typing import List
from fastapi import HTTPException
from app.models.schemas import QueryRequest, QueryResponse, AnswerChunk
from app.services.embedding_service import EmbeddingService
from app.utils.mistral_client import build_prompt, query_mistral_local

class QueryService:
    """Service for handling document queries and generating responses."""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
    
    def process_query(self, req: QueryRequest) -> QueryResponse:
        """Process user query and return AI-generated response with references."""
        try:
            # Get relevant chunks from Pinecone
            top_chunks = self.embedding_service.query_vectors(req.question, top_k=req.top_k)
            
            if not top_chunks:
                raise HTTPException(status_code=404, detail="No relevant documents found.")
            
            # Build prompt and query Mistral
            prompt = build_prompt(top_chunks, req.question)
            answer = query_mistral_local(prompt)
            
            # Format references for response
            references = []
            for chunk in top_chunks:
                references.append(
                    AnswerChunk(
                        text=chunk.get("text", ""),
                        source=chunk.get("source", "N/A"),
                        score=chunk.get("score", 0.0),
                        page=chunk.get("page"),
                        slide=chunk.get("slide"),
                        sheet=chunk.get("sheet"),
                        start_row=chunk.get("start_row"),
                        end_row=chunk.get("end_row")
                    )
                )
            
            return QueryResponse(answer=answer, references=references)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
