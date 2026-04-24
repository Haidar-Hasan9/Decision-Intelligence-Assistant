# backend/app/main.py
from fastapi import FastAPI

app = FastAPI(title="Decision Intelligence Assistant")

@app.get("/health")
async def health():
    return {"status": "ok"}