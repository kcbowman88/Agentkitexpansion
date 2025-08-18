import logging
import re
from typing import Tuple, Optional, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ObjectionHandler:
    """
    Handles user objections by identifying the type of objection from user input
    and providing a scripted response.
    """

    def __init__(self):
        """
        Initializes the ObjectionHandler with predefined objection patterns and responses.
        """
        self.objection_patterns: Dict[str, List[str]] = {
            "time": [
                r"don't have time",
                r"no time",
                r"i'm busy",
                r"in a hurry",
                r"quick"
            ],
            "send_info": [
                r"send me an email",
                r"send me information",
                r"send me something",
                r"email me"
            ],
            "not_interested": [
                r"not interested",
                r"don't need it",
                r"not looking for anything",
                r"we are good"
            ],
            "gatekeeper": [
                r"he's not here",
                r"she's not in",
                r"not available",
                r"in a meeting"
            ],
            "just_looking": [
                r"just looking",
                r"just browsing",
                r"still researching"
            ],
            "already_have_solution": [
                r"already have a solution",
                r"we use someone else",
                r"we're covered"
            ],
            "bad_experience": [
                r"bad experience",
                r"not happy with",
                r"had a problem"
            ],
            "too_expensive": [
                r"too expensive",
                r"costs too much",
                r"not in the budget"
            ]
        }

        self.objection_responses: Dict[str, str] = {
            "time": "I understand you're busy, and I'll be brief. The reason for my call is...",
            "send_info": "I can certainly send you some information. To make sure it's relevant, could you tell me a bit about...",
            "not_interested": "I hear you. Many of our best clients felt the same way at first. Just so I'm clear, what specifically are you not interested in?",
            "gatekeeper": "No problem. Could you let me know when would be a better time to reach them? Or perhaps you could help me...",
            "just_looking": "That's great to hear that you're doing your research. What have you found so far that you like?",
            "already_have_solution": "That's great. We're not looking to replace your current solution, but to complement it. Many of our clients use us for...",
            "bad_experience": "I'm sorry to hear that. We take feedback very seriously. Could you tell me a bit more about what happened?",
            "too_expensive": "I understand that budget is a major consideration. We have a range of options to fit different needs. Could we explore what might work for you?"
        }

    def handle_objection(self, user_input: str, current_node_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Analyzes user input to detect and handle objections.

        Args:
            user_input: The user's spoken text.
            current_node_id: The current node in the conversation flow.

        Returns:
            A tuple containing the response text and the objection type.
            Returns (None, None) if no objection is detected.
        """
        if not isinstance(user_input, str) or not user_input.strip():
            logging.warning("Received empty or invalid user input.")
            return None, None

        sanitized_input = user_input.lower().strip()

        for objection_type, patterns in self.objection_patterns.items():
            for pattern in patterns:
                if re.search(pattern, sanitized_input):
                    logging.info(f"Detected '{objection_type}' objection from node '{current_node_id}'.")
                    response = self.objection_responses.get(objection_type)
                    if response:
                        return response, objection_type
                    else:
                        logging.error(f"No response defined for objection type '{objection_type}'.")
                        return "I'm not sure how to respond to that.", "unknown_objection"

        logging.info(f"No specific objection detected in user input from node '{current_node_id}'.")
        return None, None

# Example usage:
if __name__ == '__main__':
    handler = ObjectionHandler()
    
    # Test cases
    test_inputs = {
        "time_objection": "I'm sorry, I just don't have time right now.",
        "info_request": "Could you just send me an email with the details?",
        "no_objection": "That sounds interesting, tell me more.",
        "empty_input": "",
        "bad_experience": "We had a bad experience with a similar service."
    }

    for name, text in test_inputs.items():
        print(f"--- Testing: {name} ---")
        print(f"Input: '{text}'")
        response, objection_type = handler.handle_objection(text, "test_node")
        print(f"Response: '{response}'")
        print(f"Objection Type: '{objection_type}'")
        print("-" * (len(name) + 14))
        print()