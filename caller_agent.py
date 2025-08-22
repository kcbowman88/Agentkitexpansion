import logging
import asyncio

from livekit.agents import Agent, JobContext, JobRequest
from livekit.agents.nodes import Router
from livekit.agents.voice import AgentSession
from livekit.plugins import openai, deepgram, elevenlabs

from state_manager import CallFlowState
from nodes import N001A_NameConfirmation_Only

async def entrypoint(job: JobContext):
    """
    The main entrypoint for the agent.
    """
    logging.info("Starting CallFlowAgent job")

    # Initialize services (STT, TTS)
    try:
        stt = deepgram.STT()
        tts = elevenlabs.TTS()
    except Exception as e:
        logging.error(f"Failed to initialize speech services: {e}")
        # In a real scenario, we might want to handle this more gracefully.
        # For now, we'll let it fail if keys are missing.
        return

    # Initial state
    state = CallFlowState(customer_name="John")
    
    # The router is the entry point of our node-based call flow
    router = CallRouter()

    # Create the agent session
    session = AgentSession(
        job.room,
        job.participant,
        stt=stt,
        tts=tts,
        userdata=state,
    )
    
    # Start the router
    await router.start(session)

class CallRouter(Router):
    def __init__(self):
        super().__init__()
        self.llm = openai.LLM()

    async def route(self, session: AgentSession) -> 'Node':
        # The conversation always starts with the name confirmation node.
        return N001A_NameConfirmation_Only(self.llm)
