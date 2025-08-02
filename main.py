from fastapi import FastAPI, Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
import uvicorn
import os

from utils.pdf_parser import download_pdf_from_url, parse_pdf_generic
from utils.embeddings import generate_embeddings
from utils.retrieval import build_faiss_index, search_faiss
from utils.llm import generate_answer_mistral

API_KEY = os.getenv("HACKRX_API_KEY", "test_api_key")

app = FastAPI(
    title="HackRX Query Retrieval System",
    description="LLM-powered intelligent query–retrieval system using Mistral + FAISS",
    version="1.0.0"
)

security = HTTPBearer()

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

@app.post("/hackrx/run", response_model=QueryResponse)
async def hackrx_run(payload: QueryRequest, credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    pdf_bytes = download_pdf_from_url(payload.documents)
    chunks = parse_pdf_generic(pdf_bytes)
    chunk_embeddings = generate_embeddings(chunks)
    index = build_faiss_index(chunk_embeddings)

    answers = []
    for question in payload.questions:
        q_embedding = generate_embeddings([question])[0]
        indices, distances = search_faiss(index, q_embedding, top_k=3)
        retrieved_chunks = [chunks[i] for i in indices]
        context = "\n".join(retrieved_chunks)
        answer = generate_answer_mistral(context, question)
        answers.append(answer)

    return QueryResponse(answers=answers)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)