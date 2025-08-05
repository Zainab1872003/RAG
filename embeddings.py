# embed_and_upsert.py
import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()
from org.doc_loader import load_and_chunk_pdf
pc = Pinecone(api_key=os.getenv("API_KEY"))
index = pc.Index("rag")

# Load the embedding model once
model = SentenceTransformer("BAAI/bge-base-en-v1.5")  # change as needed

def embed_and_upsert(chunks, metadata, batch_size=100):
    # Generate embeddings for all chunks first
    embeddings = model.encode(chunks, show_progress_bar=True)
    total = len(embeddings)
    
    # Get filename from first metadata entry (they should all be the same)
    filename = metadata[0]['source']
    
    for start_idx in range(0, total, batch_size):
        end_idx = min(start_idx + batch_size, total)
        batch_vectors = []
        
        for i in range(start_idx, end_idx):
            # Use filename + chunk index for vector ID
            vec_id = f"{filename}_{i}"
            batch_vectors.append((vec_id, embeddings[i].tolist(), metadata[i]))
        
        # Upsert the current batch to Pinecone
        index.upsert(vectors=batch_vectors)



if __name__ == "__main__":
    # Example usage - loading PDF and embedding
    pdf_chunks, pdf_metadata = load_and_chunk_pdf("./uploaded_docs/file-sample_150kB.pdf")
    embed_and_upsert(pdf_chunks, pdf_metadata)

    # # Example usage - loading DOCX and embedding
    # docx_chunks, docx_metadata = load_and_chunk_pdf("dataofdocx.pdf")
    # embed_and_upsert(docx_chunks, docx_metadata)

    print("Embedding and upsert complete!")