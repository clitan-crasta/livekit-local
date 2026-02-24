"""Minimal stub for POST /save. From repo root: server/.venv/bin/python -m uvicorn save_api_stub:app --host 127.0.0.1 --port 4000"""
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
