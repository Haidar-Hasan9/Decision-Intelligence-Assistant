from fastapi import FastAPI
from app.routers import retrieval, ml, llm

app = FastAPI(title="Decision Intelligence Assistant")

app.include_router(retrieval.router)
app.include_router(ml.router)
app.include_router(llm.router)

@app.get("/health")
async def health():
    return {"status": "ok"}