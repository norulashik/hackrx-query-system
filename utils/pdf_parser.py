import fitz  # PyMuPDF
import requests

def download_pdf_from_url(url: str) -> bytes:
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def parse_pdf_generic(pdf_bytes: bytes, max_chunk_size: int = 300) -> list:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    chunks = []
    
    # Process each page
    for page in doc:
        # Get text with better formatting
        text = page.get_text("text", sort=True)
        
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            # Skip empty paragraphs
            if not para.strip():
                continue
                
            para_length = len(para.split())
            
            # If adding this paragraph would exceed max size
            if current_length + para_length > max_chunk_size:
                # If we have accumulated content, create a chunk
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                # If paragraph is too large for a single chunk, split it
                if para_length > max_chunk_size:
                    words = para.split()
                    for i in range(0, len(words), max_chunk_size):
                        chunks.append(" ".join(words[i:i + max_chunk_size]))
                else:
                    current_chunk.append(para)
                    current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length
                
        # Add remaining chunk if any
        if current_chunk:
            chunks.append(" ".join(current_chunk))
    
    # Add overlap between chunks to maintain context
    overlapped_chunks = []
    overlap_size = int(max_chunk_size * 0.3)  # 30% overlap
    
    for i in range(len(chunks) - 1):
        # Create chunk with overlap
        combined = chunks[i] + "\n\n" + chunks[i + 1][:overlap_size]
        overlapped_chunks.append(combined)
    
    # Add the last chunk
    if chunks:
        overlapped_chunks.append(chunks[-1])
    
    return overlapped_chunks
