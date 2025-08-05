import requests

def build_prompt(chunks, user_query):
    # Combine context snippets (top chunks)
    context = "\n\n".join([c["text"] for c in chunks])
    prompt = (
        "Use the following context to answer the user's question.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {user_query}\n\n"
        "Answer:"
    )
    return prompt

def query_mistral_local(prompt, model="mistral", base_url="http://localhost:11434", max_tokens=2000):
    response = requests.post(
        f"{base_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens
            }
        },
        timeout=420,
    )
    response.raise_for_status()  # Raises exception if API call fails
    return response.json()["response"]