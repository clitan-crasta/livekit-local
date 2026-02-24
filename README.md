# LiveKit Voice Agent (self-hosted)

A local LiveKit setup with a voice AI agent that collects **name**, **age**, and **place** from the user, POSTs them to your API at `http://localhost:4000/save`, says thank you, and ends the call. Includes a web UI to start calls.

## Prerequisites

- Local LiveKit server running (API Key: `devkey`, Secret: `secret`)
- Python 3.10+
- Your backend at `http://localhost:4000/save` accepting POST with JSON body: `{ "name", "age", "place" }`

## Project layout

- **agent/** – Python voice agent (Gemini LLM, Deepgram STT/TTS). Collects name/age/place, POSTs to `/save`, then ends the call.
- **server/** – Token server (FastAPI): serves the web client and `POST /start-call` (returns LiveKit URL + token and dispatches the agent).
- **client/** – Static web UI (HTML/CSS/JS): “Start call” / “End call” and status.

## Run order

1. **Backend** – Ensure `http://localhost:4000/save` is up. Optional test stub (from repo root):  
   `server/.venv/bin/python -m uvicorn save_api_stub:app --host 127.0.0.1 --port 4000`
2. **LiveKit server** – Run `livekit-server --dev` (or use your existing instance with `devkey` / `secret`).
3. **Agent** – From `agent/`:
   ```bash
   cd agent
   uv sync   # or: pip install -e .
   uv run agent.py download-files   # first time: download Silero/VAD etc.
   uv run agent.py dev
   ```
4. **Token server** – From `server/`:
   ```bash
   cd server
   uv sync
   uv run python -m server.main   # or: uvicorn server.main:app --host 0.0.0.0 --port 8000
   ```
5. **Client** – Open `http://localhost:8000`, click “Start call”, and talk.

## Environment

**Agent** (`agent/.env.local` or env):

- `LIVEKIT_URL=ws://127.0.0.1:7880`
- `LIVEKIT_API_KEY=devkey`
- `LIVEKIT_API_SECRET=secret`
- `GOOGLE_API_KEY` – Gemini (Google AI Studio)
- `DEEPGRAM_API_KEY` – STT/TTS

**Server** (`server/.env.local` or env):

- `LIVEKIT_URL=http://127.0.0.1:7880`
- `LIVEKIT_API_KEY=devkey`
- `LIVEKIT_API_SECRET=secret`
- `AGENT_NAME=collect-agent` (optional)

## API contract

The agent sends a POST to `http://localhost:4000/save` with:

```json
{
  "name": "<string>",
  "age": "<string>",
  "place": "<string>"
}
```

Success is determined by HTTP status (2xx = success). No specific response body is required.
