# LiveKit Voice Agent

A voice call app. The agent asks for your **name**, **age**, and **place**, saves them to an API, says thank you, and hangs up. You use a web page to start and end the call.

## What you need

- **LiveKit** running locally (dev key: `devkey`, secret: `secret`)
- **Python 3.10+**
- Something that accepts the saved data at `http://localhost:4000/save`

## What’s in this repo

| Folder        | What it does |
|---------------|--------------|
| **agent/**    | Voice AI (uses Gemini + Deepgram). Asks for name, age, place, sends them to `/save`, then ends the call. |
| **server/**   | Small web server. Serves the call page and gives you a token to join a call (`POST /start-call`). |
| **client/**   | The web page: “Start call” and “End call” buttons. |
| **node-server/** | Example API that receives the data at `POST /save` (name, age, place). You can use this or your own backend. |

## How to run (in order)

1. **Save API** (so the agent has somewhere to send the data)  
   - Option A: run the Node example: `cd node-server && npm install && npm run dev`  
   - Option B: run the Python stub: `python save_api_stub.py` (from repo root, with deps installed)  
   - It should be listening on **port 4000**.

2. **LiveKit server**  
   ```bash
   livekit-server --dev
   ```
   (Uses port 7880 by default.)

3. **Agent**  
   ```bash
   cd agent
   uv sync
   uv run agent.py download-files   # only first time
   uv run agent.py dev
   ```

4. **Token server** (serves the call page and issues tokens)  
   ```bash
   cd server
   uv sync
   uv run python server.py
   ```
   (Runs on port 8000.)

5. **Use the app**  
   Open **http://localhost:8000** in your browser. Click “Start call”, talk to the agent, then click “End call”. If you don’t hear the agent, click **“Start Audio”**.

## Config (env vars)

**Agent** (`agent/.env`): LiveKit URL/keys, `GOOGLE_API_KEY` (Gemini), `DEEPGRAM_API_KEY`. Copy from `agent/.env.example`.

**Server** (`server/.env`): LiveKit URL and API key/secret. Copy from `server/.env.example`.

## What the agent sends to your API

`POST http://localhost:4000/save` with JSON:

```json
{
  "name": "<string>",
  "age": "<string>",
  "place": "<string>"
}
```

Any 2xx response means success. The response body can be anything.
