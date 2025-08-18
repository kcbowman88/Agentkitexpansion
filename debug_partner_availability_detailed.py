#!/usr/bin/env python3
import sys
import os
import logging

# Add the current directory to the path so we can import caller_agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set logging level to DEBUG
logging.basicConfig(level=logging.DEBUG)

from caller_agent import CallFlowAgent

def test_partner_availability():
    agent = CallFlowAgent()
    
    # Test the specific response that's failing
    response = "Yes, we can both be there."
    print(f"Testing response: '{response}'")
    transition = agent._get_content_based_transition("N018_ConfirmPartnerAvailability", response)
    print(f"Response: '{response}' -> Transition: '{transition}'")
    
    # Test other available responses
    available_responses = [
        "That works for us.",
        "Yes",
        "She'll be there",
        "He's free",
        "Works for us",
        "I'm the decision maker"
    ]
    
    for response in available_responses:
        print(f"Testing response: '{response}'")
        transition = agent._get_content_based_transition("N018_ConfirmPartnerAvailability", response)
        print(f"Response: '{response}' -> Transition: '{transition}'")

if __name__ == "__main__":
    test_partner_availability()