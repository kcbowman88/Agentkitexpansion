import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
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
    Evaluates whether transition conditions are met based on user responses.
    This implementation is being refactored to be more stateful and context-aware.
    """

    def __init__(self, state: CallFlowState):
        """Initializes the evaluator with the current conversation state."""
        self.state = state
        # This will be expanded to a more dynamic pattern-matching system
        self.condition_patterns = {
            "affirmative_name_confirmation": [re.compile(r'\b(yes|yep|yeah|that\'s me|it is|correct)\b', re.IGNORECASE)],
            "wrong_number_indicated": [re.compile(r'\b(wrong number|wrong person|not him|not her)\b', re.IGNORECASE)],
            "ambiguous_name_confirmation": [re.compile(r'\b(uh-huh|huh|hmm|what|who is this)\b', re.IGNORECASE)],
            "affirmative_intro_and_help_request": [re.compile(r'\b(sure|i guess|okay|what is it|go ahead|yes)\b', re.IGNORECASE)],
            "negative_intro_and_help_request": [re.compile(r'\b(no thanks|not interested|no|i\'m busy)\b', re.IGNORECASE)],
            "objection_company_question": [re.compile(r'\b(who are you|what company|who is this|where you from)\b', re.IGNORECASE)],
            "permission_granted": [re.compile(r'\b(go ahead|sure|okay|yes|what is it|fine)\b', re.IGNORECASE)],
            "no_recall": [re.compile(r'\b(don\'t recall|don\'t remember|what was that|no)\b', re.IGNORECASE)],
            "objection_or_callback_request": [re.compile(r'\b(call me back|later|another time)\b', re.IGNORECASE)],
            "not_interested": [re.compile(r'\b(not interested|no thanks|i\'m good|don\'t want|remove me)\b', re.IGNORECASE)],
            "no_time": [re.compile(r'\b(no time|i\'m busy|in a meeting)\b', re.IGNORECASE)],
            "question": [re.compile(r'\b(what is this about|what\'s this regarding|what do you want|why)\b', re.IGNORECASE)],
            "ambiguous_opener_response": [re.compile(r'\b(uh-huh|huh|hmm|okay)\b', re.IGNORECASE)],
            "curiosity_or_interest_expressed": [re.compile(r'\b(explore|curious|tell me more|how does it work|okay|yes|maybe|if it works)\b', re.IGNORECASE)],
            "callback_requested": [re.compile(r'\b(call me back|later|another time)\b', re.IGNORECASE)],
            "shows_interest": [re.compile(r'\b(yes|i am|that sounds interesting|tell me more|possibly|maybe|what\'s it about)\b', re.IGNORECASE)],
            "disinterested": [re.compile(r'\b(no|not interested|i\'m good)\b', re.IGNORECASE)],
            "general_response": [re.compile(r'\b(okay|sure|yes|yeah|alright|fine|sounds good|i see|got it|cool|straightforward|makes sense|i understand|i wouldn\'t|said i wouldn\'t)\b', re.IGNORECASE)],
        }

    def evaluate_response(self, user_input: str, transition_conditions: Dict[str, str]) -> Tuple[bool, Optional[str], str]:
        """
        Evaluate user response against transition conditions in a single, ordered pass.
        Returns the first condition that matches.
        """
        logging.debug(f"Evaluating response: '{user_input}' with conditions: {transition_conditions}")
        
        for condition_desc, target_node in transition_conditions.items():
            if self._check_condition(user_input, condition_desc):
                logging.info(f"Transition condition met: '{condition_desc}' -> {target_node}")
                return True, target_node, condition_desc

        if 'default' in transition_conditions:
            target_node = transition_conditions['default']
            logging.info(f"No specific condition met. Using default transition to {target_node}")
            return True, target_node, 'default'
            
        logging.info("No transition condition met, and no default transition available.")
        return False, None, ""

    def _check_condition(self, user_input: str, condition_desc: str) -> bool:
        """
        Checks if the user input matches a given condition description using a
        more robust, keyword-based approach. This will be refactored to be
        stateful and context-aware.
        """
        # Sanitize the input string from list-like formatting e.g., "['Hello?']"
        cleaned_input = re.sub(r"[\[\]\'\"]", "", user_input)
        input_lower = cleaned_input.lower().strip()
        desc_lower = condition_desc.lower()

        # Find the specific condition key that is a substring of the description
        matched_key = None
        for key in self.condition_patterns.keys():
            if key in desc_lower:
                matched_key = key
                break
        
        # If a specific condition is matched, check its patterns
        if matched_key:
            for pattern in self.condition_patterns[matched_key]:
                if pattern.search(input_lower):
                    return True

        return False

    def _identify_condition_type(self, condition_description: str) -> ConditionType:
        """Identify the type of condition from its description"""
        desc_lower = condition_description.lower()
        if "affirmative" in desc_lower or "permission_granted" in desc_lower or "agreed" in desc_lower:
            return ConditionType.AFFIRMATIVE
        if "negative" in desc_lower or "wrong_number" in desc_lower or "no_recall" in desc_lower or "not_interested" in desc_lower:
            return ConditionType.NEGATIVE
        if "question" in desc_lower or "company_question" in desc_lower:
            return ConditionType.QUESTION
        if "time" in desc_lower or "notime" in desc_lower:
            return ConditionType.TIME_CONSTRAINT
        if "objection" in desc_lower:
            return ConditionType.OBJECTION
        return ConditionType.DEFAULT

    def extract_transition_conditions_from_node(self, node_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract and parse transition conditions from a node's data structure
        """
        result: Dict[str, str] = {}
        if not isinstance(node_data, dict):
            return result
        tc = node_data.get("transition_conditions")
        tx = node_data.get("transitions")
        if isinstance(tc, dict) and isinstance(tx, dict):
            for key, target in tx.items():
                desc = tc.get(key, key)
                result[str(desc)] = str(target)
            if "default" in tx:
                result["default"] = str(tx["default"])
            return result
        if isinstance(tx, dict):
            for k, v in tx.items():
                result[str(k)] = str(v)
            return result
        if isinstance(tx, list):
            for item in tx:
                if isinstance(item, dict):
                    condition = item.get("condition", "default")
                    target = item.get("target", item.get("next_node", ""))
                    if target:
                        result[str(condition)] = str(target)
            if result:
                return result
        if isinstance(tc, dict):
            return {str(k): str(v) for k, v in tc.items()}
        if isinstance(tx, str):
            return self._parse_transition_string(tx)
        if isinstance(tc, str):
            return self._parse_transition_string(tc)
        return result
        
    def _parse_transition_string(self, transition_str: str) -> Dict[str, str]:
        """Parse transition conditions from string format"""
        transitions = {}
        pattern = re.compile(r'([^:]+):\s*([^\s,]+)')
        matches = pattern.findall(transition_str)
        for condition, target in matches:
            transitions[condition.strip()] = target.strip()
        return transitions

    def should_retry_node_goal(self, user_input: str, transition_conditions: Dict[str, str], 
                               current_attempts: int, max_attempts: int = 3) -> bool:
        """
        Determine if we should retry achieving the node's goal
        """
        if current_attempts >= max_attempts:
            return False
        
        condition_met, _, condition_desc = self.evaluate_response(user_input, transition_conditions)
        
        if condition_met:
            condition_type = self._identify_condition_type(condition_desc)
            if condition_type == ConditionType.QUESTION:
                return True
            else:
                return False
        
        if self.requires_specific_response(transition_conditions):
            return True
        
        return False

    def requires_specific_response(self, transition_conditions: Dict[str, str]) -> bool:
        """
        Determine if the current node requires a specific response to transition
        """
        if len(transition_conditions) == 1 and 'default' in transition_conditions:
            return False
        return True