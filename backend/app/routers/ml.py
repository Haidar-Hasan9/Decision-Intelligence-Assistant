from fastapi import APIRouter, Query
from app.services.retrieval_service import retrieve_tickets

router = APIRouter(prefix="/retrieval", tags=["retrieval"])

@router.get("/similar")
async def get_similar_tickets(query: str = Query(..., description="User query")):
    results = retrieve_tickets(query)
    return {"results": results}