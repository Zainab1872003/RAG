# app/services/embedding_service.py
import os
from typing import List
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index("rag")  # Use your Pinecone index name
        
        # Load the embedding model once
        self.model = SentenceTransformer("BAAI/bge-base-en-v1.5")  # Change model if needed

    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text chunks."""
        embeddings = self.model.encode(chunks, show_progress_bar=True)
        return embeddings

    def embed_and_upsert(self, chunks: List[str], metadata: List[dict], batch_size: int = 100):
        """Generate embeddings and upsert (upload) them in batches to Pinecone."""
        embeddings = self.embed_chunks(chunks)
        total = len(embeddings)

        filename = metadata[0].get('source', 'unknown')

        for start_idx in range(0, total, batch_size):
            end_idx = min(start_idx + batch_size, total)
            batch_vectors = []

            for i in range(start_idx, end_idx):
                vec_id = f"{filename}_{i}"
                batch_vectors.append((vec_id, embeddings[i].tolist(), metadata[i]))

            self.index.upsert(vectors=batch_vectors)

    def query_vectors(self, query_text: str, top_k: int = 3) -> List[dict]:
        """Query Pinecone index and retrieve top_k matching vectors with metadata."""
        query_emb = self.model.encode([query_text])[0]
        results = self.index.query(
            vector=query_emb.tolist(),
            top_k=top_k,
            include_metadata=True
        )
        matches = results['matches']
    # Format results (you can change this as needed)
        answers = []
        for match in matches:
            answer = {
                "text": match['metadata'].get('text', ''),
                "source": match['metadata'].get('source', ''),
                "page": match['metadata'].get('page', None),
                "score": match['score'],
                "slide":match['metadata'].get("slide"),      # PPTX
                "sheet":match['metadata'].get("sheet"),      # Excel
                "start_row":match['metadata'].get("start_row"),  # Excel
                "end_row":match['metadata'].get("end_row"),    # Excel
            }
            answers.append(answer)
        return answers

    def delete_vectors(self, vector_ids: List[str]) -> None:
        """Delete vectors from Pinecone index by their IDs."""
        if vector_ids:
            self.index.delete(ids=vector_ids)
