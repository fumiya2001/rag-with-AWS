import os
import psycopg2

from pathlib import Path
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, CrossEncoder

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}
MODEL_NAME = "all-MiniLM-L6-v2"
RERANK_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

model = SentenceTransformer(MODEL_NAME)
rerank_model = CrossEncoder(RERANK_MODEL_NAME)

def query_to_embedding(query: str):
    return model.encode(query)

def retrieve_candidates(query: str, top_k: int = 10):
    query_embedding = query_to_embedding(query)

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                        SELECT chunk, 1 - (embedding <=> '{query_embedding.tolist()}') AS cosine_similarity
                FROM embeddings
                ORDER BY cosine_similarity DESC
                LIMIT '{top_k}';
            """)
            
            results = cur.fetchall()
    
    return results


def rerank_candidates(query: str, candidates, final_k: int = 5):
    if not candidates:
        return []
    
    pairs = [(query, chunk) for chunk, _ in candidates]
    rerank_scores = rerank_model.predict(pairs)

    reranked = []
    for (row, score) in zip(candidates, rerank_scores):
        reranked.append({ "chunk": row[0], "similarity": row[1], "rerank_score": score})
    
    reranked.sort(key=lambda x: x["rerank_score"], reverse=True)    
    return reranked[:final_k]



if __name__ == "__main__":
    query = "What is the self-attention mechanism?"
    results = retrieve_candidates(query)
    
    print("Initial retrieval results:")
    for chunk, similarity in results:
        print(similarity, chunk[:100])

    rerank_results = rerank_candidates(query, results)

    print("\nReranked results:")
    for res in rerank_results:
        print(res["rerank_score"], res["similarity"], res["chunk"][:100])