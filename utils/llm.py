import requests

def generate_answer_mistral(context: str, question: str) -> str:
    prompt = f"""Answer the question based only on the context below:

Context:
{context}

Question:
{question}

Answer:"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt, "stream": False}
    )
    
    response.raise_for_status()
    return response.json()["response"].strip()
