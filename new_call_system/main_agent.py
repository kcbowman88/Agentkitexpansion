import logging
from livekit import agents
from livekit.agents import llm

from new_call_system.engine import ConversationEngine
from new_call_system.state import ConversationState

class NewCallFlowAgent(agents.Agent):
    """
    The LiveKit Agent that integrates with the new ConversationEngine.
    """
    def __init__(self):
        super().__init__()
        self.session = None

    async def on_enter(self):
        """
        Called when the agent joins the call.
        Initializes the state and engine, and starts the conversation.
        """
        try:
            # 1. Initialize State
            # In a real app, customer_name would come from context or a database.
            customer_name = "John"
            initial_state = ConversationState(
                customer_name=customer_name,
                current_node_id="N001A_NameConfirmation_Only" # Starting node
            )

            # 2. Initialize Engine
            # We need to pass the agent session to the engine so nodes can speak.
            self.engine = ConversationEngine(initial_state, self.session)

            # 3. Start the conversation
            logging.info("Starting new conversation engine...")
            await self.engine.start(initial_node_id=initial_state.current_node_id)

        except Exception as e:
            logging.error(f"Error in NewCallFlowAgent on_enter: {e}", exc_info=True)

    async def on_user_turn_completed(self, turn_ctx: llm.ChatContext, new_message: llm.ChatMessage) -> None:
        """
        Called when the user finishes speaking.
        Passes the input to the conversation engine.
        """
        try:
            user_input = str(new_message.content) if new_message.content else ""
            logging.info(f"User turn completed with text: '{user_input}'")
            if not user_input:
                return

            if self.engine:
                await self.engine.handle_user_input(user_input)
            else:
                logging.error("Engine not initialized. Cannot handle user input.")

        except Exception as e:
            logging.error(f"Error in NewCallFlowAgent on_user_turn_completed: {e}", exc_info=True)
