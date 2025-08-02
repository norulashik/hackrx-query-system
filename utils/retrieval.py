import faiss
import numpy as np

def build_faiss_index(embeddings):
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype('float32'))
    return index

def search_faiss(index, query_embedding, top_k=3):
    query_vector = np.array([query_embedding]).astype('float32')
    distances, indices = index.search(query_vector, top_k)
    return indices[0], distances[0]