from llama_index.llms.groq import Groq
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from llama_index.embeddings.jinaai import JinaEmbedding

text_embed_model = JinaEmbedding(
    api_key="jina_d191fd0ac5bf43148e846dc3d72f6fd4G9QM5K0gdVjv-5hCZ6CBk-i-9n04",
    model="jina-embeddings-v3",
    task="retrieval.passage",
)
query_embed_model = JinaEmbedding(
    api_key="jina_d191fd0ac5bf43148e846dc3d72f6fd4G9QM5K0gdVjv-5hCZ6CBk-i-9n04",
    model="jina-embeddings-v3",
    task="retrieval.query",
    dimensions=1024,
)

dimension = 1024
index = faiss.IndexFlatL2(dimension)

def read_and_split_txt(file_path, chunk_size=200):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    # Split the content into chunks (e.g., 200 words each)
    words = content.split()
    chunks = [
        " ".join(words[i : i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]
    return chunks

file_path = "sample_product_catalog.txt"

documents = read_and_split_txt(file_path)

for doc in documents:
    page_embedding = text_embed_model.get_text_embedding(doc)
    page_embedding = np.array([page_embedding], dtype="float32")
    index.add(page_embedding)

# Map document embeddings to the original text
doc_map = {i: doc for i, doc in enumerate(documents)}

# Function to retrieve top-k similar documents
def retrieve(query, k=3):
    query_embedding = query_embed_model.get_query_embedding(query)
    query_embedding = np.array([query_embedding], dtype="float32")
    distances, indices = index.search(query_embedding, k)
    return [(doc_map[idx], distances[0][i]) for i, idx in enumerate(indices[0])]
