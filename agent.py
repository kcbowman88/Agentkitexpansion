import os
import logging
import asyncio
from typing import Optional
from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import (AgentSession, RoomInputOptions, AgentStateChangedEvent)
from livekit.plugins import (
    openai,
    elevenlabs,
    deepgram,
    noise_cancellation,
    silero,
)

from new_call_system.main_agent import NewCallFlowAgent

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)

TURN_DETECTION_MODE = os.getenv("TURN_DETECTION_MODE", "auto")

async def entrypoint(ctx: agents.JobContext):
    logging.info("Starting new agent entrypoint...")

    vad = silero.VAD.load(min_silence_duration=1.0, activation_threshold=0.7)

    stt = None
    try:
        stt = deepgram.STT(model="nova-3", language="multi")
        logging.info("Deepgram STT initialized.")
    except Exception as e:
        logging.error(f"Failed to initialize Deepgram STT: {e}", exc_info=True)

    tts = None
    try:
        tts = elevenlabs.TTS(model="eleven_turbo_v2", voice_id="J5iaaqzR5zn6HFG4jV3b")
        logging.info("ElevenLabs TTS initialized.")
    except Exception as e:
        logging.error(f"Failed to initialize ElevenLabs TTS: {e}", exc_info=True)
        try:
            tts = openai.TTS(model="tts-1", voice="alloy")
            logging.info("OpenAI TTS initialized as fallback.")
        except Exception as fallback_e:
            logging.error(f"Failed to initialize OpenAI TTS as fallback: {fallback_e}", exc_info=True)

    session = AgentSession(
        stt=stt,
        tts=tts,
        vad=vad,
        turn_detection="vad" if TURN_DETECTION_MODE == "auto" else "manual",
        allow_interruptions=True,
    )
    logging.info("AgentSession initialized for the new engine.")

    agent = NewCallFlowAgent()

    @session.on("user_turn_completed")
    async def on_user_turn_completed(turn_ctx: agents.llm.ChatContext, new_message: agents.llm.ChatMessage):
        await agent.on_user_turn_completed(turn_ctx, new_message)

    @session.on("agent_started")
    async def on_agent_started(ev: AgentStateChangedEvent):
        # Pass the session to the agent's on_enter method
        await agent.on_enter(session)


    logging.info("Starting AgentSession with the new engine...")
    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    logging.info("AgentSession started.")

    await ctx.connect()
    logging.info("Context connected.")


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )