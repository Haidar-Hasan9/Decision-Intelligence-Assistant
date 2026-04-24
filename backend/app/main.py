from fastapi import FastAPI
from app.routers import retrieval, ml, llm
from .logging_config import setup_logging

# Setup logging before creating the app
setup_logging()

app = FastAPI(title="Decision Intelligence Assistant")

app.include_router(retrieval.router)
app.include_router(ml.router)
app.include_router(llm.router)

@app.get("/health")
async def health():
    return {"status": "ok"}