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
    
    # Test available responses
    available_responses = [
        "Yes, we can both be there.",
        "That works for us.",
        "Yes",
        "She'll be there",
        "He's free",
        "Works for us",
        "I'm the decision maker"
    ]
    
    print("Testing available responses:")
    for response in available_responses:
        transition = agent._get_content_based_transition("N018_ConfirmPartnerAvailability", response)
        print(f"Response: '{response}' -> Transition: '{transition}'")
    
    # Test not available responses
    not_available_responses = [
        "That won't work for my partner",
        "She can't",
        "He's busy",
        "No"
    ]
    
    print("\nTesting not available responses:")
    for response in not_available_responses:
        transition = agent._get_content_based_transition("N018_ConfirmPartnerAvailability", response)
        print(f"Response: '{response}' -> Transition: '{transition}'")
    
    # Test unsure responses
    unsure_responses = [
        "I don't know her schedule",
        "I'll have to check with him",
        "I don't know",
        "I'll have to check",
        "I'm not sure"
    ]
    
    print("\nTesting unsure responses:")
    for response in unsure_responses:
        transition = agent._get_content_based_transition("N018_ConfirmPartnerAvailability", response)
        print(f"Response: '{response}' -> Transition: '{transition}'")

if __name__ == "__main__":
    test_partner_availability()