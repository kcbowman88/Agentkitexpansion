import asyncio
import inspect
from typing import Optional, Type, Dict

from new_call_system.state import ConversationState
from new_call_system import nodes as nodes_module # Import the module itself

class ConversationEngine:
    """
    The core engine that drives the conversation forward.
    It manages the conversation state and the lifecycle of nodes.
    """

    def __init__(self, state: ConversationState, agent_session):
        self.state = state
        self.agent_session = agent_session
        self.node_map = self._discover_nodes()
        self.current_node: Optional[nodes_module.Node] = None

    def _discover_nodes(self) -> Dict[str, Type[nodes_module.Node]]:
        """
        Finds all Node subclasses within the nodes module and maps their class name to the class itself.
        """
        node_map = {}
        for name, obj in inspect.getmembers(nodes_module):
            if inspect.isclass(obj) and issubclass(obj, nodes_module.Node) and obj is not nodes_module.Node:
                node_map[name] = obj
        return node_map

    async def start(self, initial_node_id: str):
        """Starts the conversation engine."""
        print(f"Starting engine. Discovered nodes: {list(self.node_map.keys())}")
        await self.transition_to(initial_node_id)

    async def handle_user_input(self, user_input: str):
        """
        Handles incoming user input by passing it to the current node.
        """
        if self.current_node:
            self.state.log_utterance('user', user_input, self.state.current_node_id)
            next_node_id = await self.current_node.handle_response(user_input)
            if next_node_id:
                await self.transition_to(next_node_id)
        else:
            print("Error: No current node to handle user input.")


    async def transition_to(self, node_id: str):
        """Transitions the conversation to a new node."""
        if node_id in self.node_map:
            self.state.current_node_id = node_id
            node_class = self.node_map[node_id]
            self.current_node = node_class(self, self.state)
            print(f"Transitioning to node: {node_id}")
            await self.current_node.enter_node()
        else:
            print(f"Error: Node '{node_id}' not found in discovered nodes.")
            # In a real system, we might transition to an error-handling node.
            # For now, we'll stop.
            self.current_node = None


    async def speak(self, text: str):
        """Sends text to the TTS for the agent to speak."""
        text_to_speak = text.replace("{{customer_name}}", self.state.customer_name)

        # Log before speaking
        self.state.log_utterance('agent', text_to_speak, self.state.current_node_id)

        if self.agent_session and hasattr(self.agent_session, 'say'):
            await self.agent_session.say(text_to_speak, allow_interruptions=True)
        else:
            print(f"AGENT SAYS: {text_to_speak}") # Fallback for testing
