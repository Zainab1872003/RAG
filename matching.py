
from org.embeddings import model
from org.embeddings import index

def get_query_embedding(query_text):
    # Use your embedding model (same as used for documents)
    return model.encode([query_text])[0]

def query_pinecone(user_query, top_k=3):
    query_emb = get_query_embedding(user_query)
    results = index.query(
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