"""Minimal stub for POST /save - run with: uv run python save-api-stub.py (from repo root with fastapi/uvicorn)."""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SavePayload(BaseModel):
    name: str
    age: str
    place: str

@app.post("/save")
def save(data: SavePayload):
    print("SAVE received:", data.model_dump())
    return {"ok": True}
