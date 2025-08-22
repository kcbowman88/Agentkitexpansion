import logging
import os
import re
from typing import Optional, Dict, Any

from livekit.agents import llm
from livekit.agents.nodes import Node, Router
from livekit.agents.voice import SynthesisEvent
from state_manager import CallFlowState

class BaseNode(Node):
    def __init__(self, node_id: str, llm: llm.LLM, router: 'Router'):
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

        node_data = {'id': self.node_id, 'raw_content': content}

        # Extract Goal
        goal_match = re.search(r'## 1\. Primary Goal for This Node\s*(.*?)(?=\n##|$)', content, re.DOTALL | re.IGNORECASE)
        if goal_match:
            node_data['goal'] = goal_match.group(1).strip()

        # Extract Opening Gambit
        gambit_match = re.search(r'AGENT SAYS:\s*<speak>(.*?)</speak>', content, re.DOTALL)
        if gambit_match:
            gambit = re.sub(r'<.*?>', '', gambit_match.group(1))
            node_data['opening_gambit'] = gambit.strip()

        # Extract Transitions from the natural language description
        transitions_text = ""
        # Find the "Transition:" or "Transitions:" or "Transitioning:" section
        transitions_match = re.search(r'Transitions?ing?:\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if transitions_match:
            transitions_text = transitions_match.group(1)

        if transitions_text:
            # This regex is designed to capture the multi-line "Condition"
            transitions = re.findall(r'\*\s*Transition Name:\s*`?(.*?)`?\s*\n\s*\*\s*Condition:\s*(.*?)(?=\n\n|\n\s*\*\s*Transition Name:|\Z)', transitions_text, re.DOTALL)
            parsed_transitions = []
            for name, cond in transitions:
                # A transition might point to multiple nodes, but we'll take the first for now
                target_match = re.search(r'Next Node:\s*`?(.*?)`?', cond, re.IGNORECASE)
                target = target_match.group(1).strip() if target_match else None
                parsed_transitions.append({'name': name.strip(), 'condition': cond.strip(), 'target': target})
            node_data['transitions'] = parsed_transitions

        return node_data

    async def _determine_next_node(self, session: 'AgentSession', user_input: str) -> Optional[str]:
        """
        Uses an LLM to determine the next node based on the user's input and transition rules.
        """
        transitions = self.node_data.get('transitions', [])
        if not transitions:
            logging.info(f"Node {self.node_id} has no defined transitions.")
            return None

        transition_options = ""
        for i, transition in enumerate(transitions):
            transition_options += f"{i+1}. {transition['name']}: {transition['condition']}\n"

        prompt = f"""
        You are a "Transition Referee" for a conversational AI agent. Your task is to determine which transition to take based on the user's response.
        Respond with only the number corresponding to the best transition. If no transition is a good fit, respond with "None".

        - **Node's Goal:** {self.node_data.get('goal', 'Not specified.')}
        - **User's Response:** "{user_input}"

        **Available Transitions:**
        {transition_options}

        Which transition should be taken?
        """

        try:
            chat_response = await self.llm.chat.create(prompt=prompt)
            result = chat_response.choices[0].message.content.strip()
            logging.debug(f"Transition Referee LLM chose: '{result}'")

            if result.isdigit():
                choice_index = int(result) - 1
                if 0 <= choice_index < len(transitions):
                    return transitions[choice_index].get('target')

            return None
        except Exception as e:
            logging.error(f"LLM call failed during transition evaluation: {e}")
            return None

    async def _find_matching_tactic(self, user_input: str) -> Optional[str]:
        """
        Uses an LLM to find the best-matching pre-scripted tactic for a user's input.
        """
        toolkit = self.node_data.get('strategic_toolkit', {})
        if not toolkit:
            return None

        tactic_descriptions = list(toolkit.keys())

        prompt = f"""
        You are a "Tactic Matcher" for a conversational AI agent. Your goal is to select the best pre-scripted tactic to respond to the user's latest message.

        **User's Message:** "{user_input}"

        **Available Tactic Descriptions:**
        {tactic_descriptions}

        **Instructions:**
        Based on the user's message, which is the most appropriate tactic? Respond with only the description of the best tactic (e.g., "TRUST / SCAM Objection"). If no tactic is a good fit, respond with the word "None".
        """

        try:
            chat_response = await self.llm.chat.create(prompt=prompt)
            best_tactic_name = chat_response.choices[0].message.content.strip()
            logging.info(f"Tactic Matcher LLM chose: '{best_tactic_name}'")

            if best_tactic_name in toolkit:
                return toolkit[best_tactic_name]

            return None
        except Exception as e:
            logging.error(f"LLM call failed during tactic matching: {e}")
            return None

    async def process(self, session: 'AgentSession') -> Optional['Node']:
        logging.info(f"Executing node: {self.node_id}")
        state: CallFlowState = session.userdata

        # Speak the opening gambit only on the first entry to the node
        if not self.node_data.get('has_spoken_gambit'):
            gambit = self.node_data.get('opening_gambit')
            if gambit:
                gambit = gambit.replace("{{customer_name}}", state.customer_name)
                await session.say(gambit)
            self.node_data['has_spoken_gambit'] = True # Mark as spoken

        while True:
            try:
                user_input = await session.user_input_stream().__anext__()
                logging.info(f"User input received: {user_input.text}")

                # 1. Check for a matching tactic
                tactic_script = await self._find_matching_tactic(user_input.text)
                if tactic_script:
                    logging.info("Found matching tactic. Speaking script and staying in node.")
                    await session.say(tactic_script)
                    continue # Loop back to listen for the next user input

                # 2. If no tactic, check for a transition
                next_node_id = await self._determine_next_node(session, user_input.text)
                if next_node_id:
                    logging.info(f"Transitioning to node: {next_node_id}")
                    return self.router.create_node(next_node_id)

                # 3. If no tactic and no transition, handle fallback
                logging.warning("No matching tactic or transition found for user input.")
                await session.say("I'm not sure how to handle that. Let's try something else.")
                # In a real scenario, we might escalate to a human or a different recovery node.
                # For now, we end the conversation.
                return None

            except StopAsyncIteration:
                logging.warning("User input stream ended. Closing session.")
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
