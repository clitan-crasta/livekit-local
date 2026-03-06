"""
Token server: serves the web client and exposes POST /start-call to get a token
and dispatch the collect-agent to a new room.
"""
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

load_dotenv(".env.local")
load_dotenv()

# LiveKit URL for API (http) and for client (ws)
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "http://127.0.0.1:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")
AGENT_NAME = os.getenv("AGENT_NAME", "collect-agent")

# WebSocket URL for browser client (convert http -> ws if needed)
def _ws_url() -> str:
    if LIVEKIT_URL.startswith("http://"):
        return LIVEKIT_URL.replace("http://", "ws://", 1)
    if LIVEKIT_URL.startswith("https://"):
        return LIVEKIT_URL.replace("https://", "wss://", 1)
    if not LIVEKIT_URL.startswith("ws"):
        return f"ws://{LIVEKIT_URL}"
    return LIVEKIT_URL


app = FastAPI(title="LiveKit Token Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static client from ../../client (repo root / client)
CLIENT_DIR = Path(__file__).resolve().parent.parent.parent / "client"
if CLIENT_DIR.exists():
    app.mount("/assets", StaticFiles(directory=CLIENT_DIR), name="assets")


@app.get("/")
async def index():
    """Serve the client index.html."""
    index_file = CLIENT_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "LiveKit token server. Use POST /start-call to get a token."}


@app.post("/start-call")
async def start_call():
    """
    Create a unique room, dispatch the collect-agent to it, and return
    a participant token and WebSocket URL for the client.
    """
    from livekit import api

    room_name = f"call-{uuid.uuid4().hex[:12]}"
    participant_identity = f"user-{uuid.uuid4().hex[:8]}"

    lkapi = api.LiveKitAPI(
        url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
    )
    try:
        # Dispatch agent to the room (creates room if needed)
        await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=AGENT_NAME,
                room=room_name,
            )
        )
        # Participant token to join the room
        token = (
            api.AccessToken(api_key=LIVEKIT_API_KEY, api_secret=LIVEKIT_API_SECRET)
            .with_identity(participant_identity)
            .with_name("Guest")
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                )
            )
            .to_jwt()
        )
        return {
            "url": _ws_url(),
            "token": token,
            "room_name": room_name,
        }
    finally:
        await lkapi.aclose()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
