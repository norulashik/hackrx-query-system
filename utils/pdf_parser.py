import fitz  # PyMuPDF
import requests

def download_pdf_from_url(url: str) -> bytes:
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def parse_pdf_generic(pdf_bytes: bytes, max_chunk_size: int = 300) -> list:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    words = full_text.split()
    chunks = []
    for i in range(0, len(words), max_chunk_size):
        chunk = " ".join(words[i:i + max_chunk_size])
        chunks.append(chunk)

    return chunks
