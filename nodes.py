import logging
import os
import re
from typing import Optional, Dict, Any

from livekit.agents import llm
from livekit.agents.nodes import Node, Router
from livekit.agents.voice import SynthesisEvent
from state_manager import CallFlowState

class BaseNode(Node):
    def __init__(self, node_id: str, llm: llm.LLM, router: Router):
        super().__init__()
        self.node_id = node_id
        self.llm = llm
        self.router = router
        self.node_data = self._load_and_parse_node_file()

    def _load_and_parse_node_file(self) -> Optional[Dict[str, Any]]:
        file_path = f"prompts/nodes/{self.node_id}.md"
        if not os.path.exists(file_path):
            logging.error(f"Node file not found: {file_path}")
            return None

        with open(file_path, 'r') as f:
            content = f.read()

        # This parser can be made more robust, but it handles the current format.
        node_data = {'id': self.node_id, 'raw_content': content}

        # Extract Goal
        goal_match = re.search(r'## 1\. Primary Goal for This Node\s*(.*?)(?=\n##|$)', content, re.DOTALL | re.IGNORECASE)
        if goal_match:
            node_data['goal'] = goal_match.group(1).strip()

        # Extract Opening Gambit
        gambit_match = re.search(r'AGENT SAYS:\s*<speak>(.*?)</speak>', content, re.DOTALL)
        if gambit_match:
            # Clean up the SSML for now
            gambit = re.sub(r'<.*?>', '', gambit_match.group(1))
            node_data['opening_gambit'] = gambit.strip()

        node_data['full_prompt'] = content
        return node_data

    async def process(self, session: 'AgentSession') -> Optional['Node']:
        logging.info(f"Executing node: {self.node_id}")
        state: CallFlowState = session.userdata

        # 1. Speak the opening gambit
        gambit = self.node_data.get('opening_gambit')
        if gambit:
            gambit = gambit.replace("{{customer_name}}", state.customer_name)
            await session.say(gambit)

        # 2. Wait for user input
        try:
            user_input = await session.user_input_stream().__anext__()
            logging.info(f"User input received: {user_input.text}")
        except StopAsyncIteration:
            logging.warning("User input stream ended. Closing session.")
            return None # End of conversation

        # 3. (Placeholder) Log the input and end the flow for this first pass.
        # The next steps will involve adding the logic to handle this input.
        logging.info(f"Received user input: '{user_input.text}'. End of flow for now.")
        await session.say(f"I heard you say: {user_input.text}. The logic to handle this is not yet implemented.")

        # Returning None ends the router loop
        return None

# --- Concrete Node Implementations ---

class N001A_NameConfirmation_Only(BaseNode):
    def __init__(self, llm: llm.LLM, router: Router):
        super().__init__(node_id="N001A_NameConfirmation_Only", llm=llm, router=router)

# We can now define all other nodes just by creating a class for them.
# The router will be responsible for instantiating the correct one.
class N001B_IntroAndHelpRequest_Only(BaseNode):
    def __init__(self, llm: llm.LLM, router: Router):
        super().__init__(node_id="N001B_IntroAndHelpRequest_Only", llm=llm, router=router)
