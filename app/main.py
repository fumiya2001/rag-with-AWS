from fastapi import FastAPI
from pydantic import BaseModel
from app.search import retrieve_candidates, rerank_candidates
from app.generate import generate_answer

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
def ask(req: QueryRequest):
    candidates = retrieve_candidates(req.query)
    reranked_result = rerank_candidates(req.query, candidates)
    contexts = [res["chunk"] for res in reranked_result]
    answer = generate_answer(req.query, contexts)

    sources = [
        {
            "chunk": res["chunk"],
            "score": res["similarity"]
        }
        for res in reranked_result
    ]
    return {
        "query": req.query,
        "answer": answer,
        "sources": sources
    }