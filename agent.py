import os
import logging
import asyncio
import traceback
from dotenv import load_dotenv
from typing import Optional

from livekit import agents, rtc
from livekit.agents import (AgentSession, Agent, RoomInputOptions,
                           AgentStateChangedEvent)
from livekit.plugins import (
    openai,
    elevenlabs,
    deepgram,
    noise_cancellation,
    silero,
)
from state_manager import CallFlowState
from caller_agent import CallFlowAgent
from pivot_controller import pivot_controller # Import pivot_controller

load_dotenv()

# Set up logging to DEBUG level for detailed output
logging.basicConfig(level=logging.DEBUG)

# Configuration for turn detection mode
# "manual" for production with frontend controls, "auto" for console testing
TURN_DETECTION_MODE = os.getenv("TURN_DETECTION_MODE", "auto")

async def entrypoint(ctx: agents.JobContext):
    # Initialize state with a default customer name if not provided
    customer_name = os.getenv("CUSTOMER_NAME", "John")
    state = CallFlowState(customer_name=customer_name)
    
    # Log the initialization
    logging.info(f"CallFlowState initialized with customer_name: {state.customer_name}")
    
    # Configure turn detection based on mode
    logging.info(f"TURN_DETECTION_MODE set to: {TURN_DETECTION_MODE}")
    if TURN_DETECTION_MODE == "manual":
        turn_detection = "manual"
    else:
        turn_detection = "vad"  # Use VAD-only turn detection for more predictable behavior
    logging.info(f"Turn detection configured as: {turn_detection}")

    # Create a single VAD configuration with parameters that balance turn detection and interruption handling
    vad = silero.VAD.load(min_silence_duration=1.0, activation_threshold=0.7)

    # Initialize STT with error handling
    stt = None
    try:
        logging.info("Attempting to initialize Deepgram STT...")
        stt = deepgram.STT(model="nova-3", language="multi")
        logging.info("Deepgram STT initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize Deepgram STT: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        logging.warning("STT will be disabled. Agent may not function correctly without speech-to-text.")

    # Initialize TTS with error handling and fallback
    tts = None
    try:
        logging.info("Attempting to initialize ElevenLabs TTS...")
        tts = elevenlabs.TTS(model="eleven_turbo_v2", voice_id="J5iaaqzR5zn6HFG4jV3b")
        logging.info("ElevenLabs TTS initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize ElevenLabs TTS: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        logging.warning("Attempting to use OpenAI TTS as fallback...")
        try:
            tts = openai.TTS(model="tts-1", voice="alloy")
            logging.info("OpenAI TTS initialized as fallback")
        except Exception as fallback_e:
            logging.error(f"Failed to initialize OpenAI TTS as fallback: {fallback_e}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            logging.warning("TTS will be disabled. Agent will only work with text output.")
    
    session = AgentSession(
        stt=stt,
        tts=tts,
        vad=vad,
        turn_detection=turn_detection,
        allow_interruptions=False,  # Disable interruptions to enforce turn-based interaction
        min_interruption_duration=0.5,  # Increase to prevent single-word interruptions
        min_endpointing_delay=1.0,
        max_endpointing_delay=2.0,
        userdata=state,
    )
    logging.info("AgentSession initialized with provided STT, TTS, VAD, and turn detection settings.")

    agent = CallFlowAgent(initial_state=state)
    agent.session = session
    logging.info("CallFlowAgent initialized and session assigned.")

    # Only disable audio input at start when in manual mode
    if TURN_DETECTION_MODE == "manual":
        session.input.set_audio_enabled(False)

        # Register RPC methods only in manual mode
        # When user starts speaking
        @ctx.room.local_participant.register_rpc_method("start_turn")
        async def start_turn(data: rtc.RpcInvocationData):
            logging.info("RPC Method 'start_turn' called.")
            session.interrupt()  # Stop any current agent speech
            session.clear_user_turn()  # Clear any previous input
            session.input.set_audio_enabled(True)  # Start listening
            logging.info("Agent interrupted, user turn cleared, audio input enabled.")

        # When user finishes speaking
        @ctx.room.local_participant.register_rpc_method("end_turn")
        async def end_turn(data: rtc.RpcInvocationData):
            logging.info("RPC Method 'end_turn' called.")
            session.input.set_audio_enabled(False)  # Stop listening
            session.commit_user_turn()  # Process the input and generate response
            logging.info("Audio input disabled, user turn committed.")

        # When user cancels their turn
        @ctx.room.local_participant.register_rpc_method("cancel_turn")
        async def cancel_turn(data: rtc.RpcInvocationData):
            logging.info("RPC Method 'cancel_turn' called.")
            session.input.set_audio_enabled(False)  # Stop listening
            session.clear_user_turn()  # Discard the input
            logging.info("Audio input disabled, user turn cleared (cancelled).")

    # Track agent speaking state
    agent_is_speaking = False
    user_turn_debounce_task: Optional[asyncio.Task] = None

    # Monitor agent state changes for debugging
    @session.on("agent_state_changed")
    def on_agent_state_changed(ev: AgentStateChangedEvent):
        nonlocal agent_is_speaking, user_turn_debounce_task
        
        if ev.new_state == "initializing":
            print("Agent is starting up")
        elif ev.new_state == "idle":
            print("Agent is ready but not processing")
            agent_is_speaking = False
        elif ev.new_state == "listening":
            print("Agent is listening for user input")
            # If agent starts listening, cancel any pending debounce task
            if user_turn_debounce_task and not user_turn_debounce_task.done():
                logging.info("Cancelling pending user turn debounce task as agent started listening.")
                user_turn_debounce_task.cancel()
                user_turn_debounce_task = None
            agent_is_speaking = False
        elif ev.new_state == "thinking":
            print("Agent is processing user input and generating a response")
            # If agent starts speaking, cancel any pending debounce task
            if user_turn_debounce_task and not user_turn_debounce_task.done():
                logging.info("Cancelling pending user turn debounce task as agent started speaking.")
                user_turn_debounce_task.cancel()
                user_turn_debounce_task = None
            agent_is_speaking = False
            # Play a thinking sound (disabled)
            # asyncio.create_task(play_thinking_sound())
        elif ev.new_state == "speaking":
            print("Agent started speaking")
            agent_is_speaking = True

    @session.on("user_turn_finished")
    def on_user_turn_finished(ev: Exception):
        nonlocal user_turn_debounce_task
        
        async def _handle_turn():
            logging.info(f"User turn finished event: transcript='{ev.text}', is_final={ev.is_final}, duration={ev.duration}")

            if TURN_DETECTION_MODE == "auto":
                if not ev.is_final and pivot_controller.pivot_open:
                    # If ASR is not final and a pivot is open, debounce the turn processing
                    logging.info(f"Partial ASR result and pivot open. Debouncing user turn processing for {ev.text[:20]}...")
                    if user_turn_debounce_task and not user_turn_debounce_task.done():
                        user_turn_debounce_task.cancel()
                    
                    async def _debounced_commit():
                        try:
                            await asyncio.sleep(0.8) # Debounce window: 800ms
                            if not user_turn_debounce_task.cancelled():
                                logging.info(f"Debounce complete for partial ASR: '{ev.text}'. Committing turn.")
                                session.commit_user_turn()
                        except asyncio.CancelledError:
                            logging.info("Debounced commit task cancelled.")
                    
                    user_turn_debounce_task = asyncio.create_task(_debounced_commit())
                else:
                    # If ASR is final or no pivot is open, commit immediately
                    logging.info(f"Final ASR result or no pivot open. Committing turn for '{ev.text}'.")
                    session.commit_user_turn()
            elif TURN_DETECTION_MODE == "manual":
                # In manual mode, commit_user_turn is handled by RPC 'end_turn'
                logging.debug("Manual turn detection mode, user_turn_finished event handled by RPC.")
                if user_turn_debounce_task and not user_turn_debounce_task.done():
                    logging.info("Cancelling pending user turn debounce task as agent started speaking.")
                    user_turn_debounce_task.cancel()
                    user_turn_debounce_task = None

        asyncio.create_task(_handle_turn())

    # The enhanced features will be integrated with the existing CallFlowAgent
    # which already handles user responses through the LLM transition system

    logging.info("Starting AgentSession...")
    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    logging.info("AgentSession started.")

    logging.info("Connecting to context...")
    await ctx.connect()
    logging.info("Context connected.")


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )