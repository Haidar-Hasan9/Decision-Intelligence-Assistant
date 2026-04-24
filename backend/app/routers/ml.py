from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ml_service import predict_priority

router = APIRouter(prefix="/ml", tags=["ml"])

class PriorityRequest(BaseModel):
    text: str

@router.post("/predict")
async def predict(request: PriorityRequest):
    """Return ML priority prediction + confidence."""
    result = predict_priority(request.text)
    return result