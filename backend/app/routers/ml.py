from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ml_service import predict_priority, load_model_metadata

router = APIRouter(prefix="/ml", tags=["ml"])

class PriorityRequest(BaseModel):
    text: str

@router.post("/predict")
async def predict(request: PriorityRequest):
    result = predict_priority(request.text)
    return result

@router.get("/info")
async def get_model_info():
    meta = load_model_metadata()
    return {
        "test_f1": meta.get("test_f1"),
        "test_roc_auc": meta.get("test_roc_auc")
    }