from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import (
    generate_answer_with_rag, generate_answer_no_rag, predict_priority_zero_shot
)
from app.services.retrieval_service import retrieve_tickets

router = APIRouter(prefix="/llm", tags=["llm"])

class QueryRequest(BaseModel):
    query: str

@router.post("/rag")
async def rag_answer(request: QueryRequest):
    # Retrieve context
    retrieved = retrieve_tickets(request.query)
    context = "\n".join([f"- {r['document']}" for r in retrieved])
    result = generate_answer_with_rag(request.query, context)
    return {
        "answer": result["answer"],
        "sources": retrieved,
        "latency_ms": result["latency_ms"],
        "cost_usd": result["cost_usd"]
    }

@router.post("/non-rag")
async def non_rag_answer(request: QueryRequest):
    result = generate_answer_no_rag(request.query)
    return {
        "answer": result["answer"],
        "latency_ms": result["latency_ms"],
        "cost_usd": result["cost_usd"]
    }

@router.post("/priority")
async def llm_priority(request: QueryRequest):
    result = predict_priority_zero_shot(request.query)
    return result