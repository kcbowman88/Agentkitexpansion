import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from livekit.agents import llm

if "CallFlowState" not in locals():
    from state_manager import CallFlowState

class ConditionType(Enum):
    """Types of transition conditions"""
    AFFIRMATIVE = "affirmative"
    NEGATIVE = "negative"
    QUESTION = "question"
    TIME_CONSTRAINT = "time_constraint"
    OBJECTION = "objection"
    DEFAULT = "default"

class TransitionEvaluator:
    """
    Evaluates whether transition conditions are met based on user responses using LLM-based semantic analysis.
    """

    def __init__(self, state: CallFlowState, llm: llm.LLM):
        """Initializes the evaluator with the current conversation state and an LLM instance."""
        self.state = state
        self.llm = llm

    async def evaluate_response(self, user_input: str, node_data: Dict[str, Any]) -> Tuple[bool, Optional[str], str]:
        """
        Evaluate user response against transition conditions in a single, ordered pass.
        Returns the first condition that matches.
        """
        node_goal = node_data.get('goal', 'Not specified.')
        transitions = node_data.get('transitions', [])

        logging.debug(f"Evaluating response: '{user_input}' for node '{node_data.get('id')}'")
        
        for transition in transitions:
            condition_desc = transition.get("condition")
            target_node = transition.get("target")
            # The detailed description is now the primary source for semantic matching
            semantic_desc = transition.get("description", condition_desc)

            if await self._check_condition_semantically(user_input, node_goal, semantic_desc):
                logging.info(f"Semantic transition condition met: '{condition_desc}' -> {target_node}")
                return True, target_node, condition_desc

        # Find a default transition if no semantic match
        for transition in transitions:
            if transition.get("condition") == "default":
                target_node = transition.get("target")
                logging.info(f"No specific condition met. Using default transition to {target_node}")
                return True, target_node, 'default'
            
        logging.info("No transition condition met, and no default transition available.")
        return False, None, ""

    async def _check_condition_semantically(self, user_input: str, node_goal: str, condition_description: str) -> bool:
        """
        Uses an LLM to check if the user input semantically matches a given condition.
        """
        prompt = f"""
        You are a "Transition Referee" for a conversational AI agent. Your task is to determine if the user's response satisfies a specific transition condition.
        Respond with only "true" or "false".

        - **Node's Goal:** {node_goal}
        - **User's Response:** "{user_input}"
        - **Transition Condition to Check:** "{condition_description}"

        Does the user's response semantically satisfy the transition condition?
        """
        
        try:
            chat_response = await self.llm.chat.create(prompt=prompt)
            result = chat_response.choices[0].message.content.strip().lower()
            logging.debug(f"Semantic check for '{condition_description}': LLM responded with '{result}'")
            return result == "true"
        except Exception as e:
            logging.error(f"LLM call failed during semantic check for condition '{condition_description}': {e}")
            return False

    async def should_retry_node_goal(self, user_input: str, node_data: Dict[str, Any],
                                     current_attempts: int, max_attempts: int = 3) -> bool:
        """
        Determine if we should retry achieving the node's goal.
        This now simply checks if a transition condition was met. If not, we should retry.
        """
        if current_attempts >= max_attempts:
            logging.warning(f"Max attempts ({max_attempts}) reached for node {node_data.get('id')}. Not retrying.")
            return False
        
        condition_met, _, _ = await self.evaluate_response(user_input, node_data)
        
        # If no condition was met, we should retry the node's goal.
        return not condition_met