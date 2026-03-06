"""
LiveKit voice agent that collects name, age, and place from the user,
POSTs to http://localhost:4000/save, says thank you, and ends the call.
"""
import logging
import os
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession, AgentServer, JobContext, RunContext, function_tool, room_io
from livekit.plugins import deepgram, google, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv(".env.local")
load_dotenv()

logger = logging.getLogger("collect-agent")

SAVE_URL = os.getenv("SAVE_API_URL", "http://localhost:4000/save")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


class CollectAgent(Agent):
    """Agent that collects name, age, and place then submits to API and ends the call."""

    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly voice assistant. Your only job is to collect three pieces of information from the user:
1. Their name
2. Their age (can be a number or spoken like "twenty-five")
3. Their place (where they live or are from)

Ask for these in a natural, conversational way. You may ask in any order. Once you have all three (name, age, and place), you MUST call the submit_user_details tool with those three values. Do not call the tool until you have all three. Keep responses concise and without emojis or special formatting.""",
        )

    @function_tool()
    async def submit_user_details(
        self,
        ctx: RunContext,
        name: str,
        age: str,
        place: str,
    ) -> str | None:
        """Submit the collected user details. Call this only when you have the user's name, age, and place.

        Args:
            name: The user's name.
            age: The user's age (as they said it, e.g. "25" or "twenty-five").
            place: The user's place (where they live or are from).
        """
        payload = {"name": name, "age": age, "place": place}
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    SAVE_URL,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status >= 400:
                        logger.warning("Save API returned %s: %s", resp.status, await resp.text())
                        return f"Save failed with status {resp.status}. Ask the user to try again or say goodbye."
            # Success: say thank you then end the call
            await ctx.wait_for_playout()
            handle = ctx.session.say(
                "Thank you for the details. Goodbye!",
                allow_interruptions=False,
            )
            if handle:
                handle.add_done_callback(lambda _: _shutdown_after_speech(ctx))
            else:
                ctx.session.shutdown()
            return None
        except Exception as e:
            logger.exception("Error calling save API: %s", e)
            return "Sorry, we could not save your details. Please try again later or say goodbye."


def _shutdown_after_speech(ctx: RunContext) -> None:
    try:
        ctx.session.shutdown()
    except Exception:
        pass


server = AgentServer()

// check 
@server.rtc_session(agent_name="collect-agent")
async def collect_agent(ctx: JobContext) -> None:
    session = AgentSession(
        stt=deepgram.STT(model="nova-2", language="en"),
        llm=google.LLM(model=GEMINI_MODEL),
        tts=deepgram.TTS(model="aura-asteria-en"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
    await session.start(
        room=ctx.room,
        agent=CollectAgent(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )
    await session.generate_reply(
        instructions="Greet the user briefly and ask for their name, then their age, then where they are from. Collect all three before submitting.",
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
