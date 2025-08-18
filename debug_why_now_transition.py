#!/usr/bin/env python3
"""
Debug script for N401_AskWhyNow_Initial_V10_AssertiveFrame transition logic.
"""

import sys
import os

# Add the current directory to the path so we can import caller_agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from caller_agent import CallFlowAgent

def debug_why_now_transition():
    """Debug the N401_AskWhyNow_Initial_V10_AssertiveFrame node transition."""
    print("Debugging N401_AskWhyNow_Initial_V10_AssertiveFrame transition...")
    
    agent = CallFlowAgent()
    
    # Test the specific response that's failing
    test_response = "I'm just tired of the 9-to-5 and need more freedom."
    print(f"Testing motivation response: '{test_response}'")
    
    transition = agent._get_content_based_transition("N401_AskWhyNow_Initial_V10_AssertiveFrame", test_response)
    print(f"Transition result: '{transition}'")
    
    # Test callback response
    callback_response = "I have to go now."
    print(f"\nTesting callback response: '{callback_response}'")
    
    transition = agent._get_content_based_transition("N401_AskWhyNow_Initial_V10_AssertiveFrame", callback_response)
    print(f"Transition result: '{transition}'")
    
    # Let's also check what the motivation indicators are
    from call_flow import nodes
    current_node = nodes.get("N401_AskWhyNow_Initial_V10_AssertiveFrame")
    if current_node:
        print(f"\nNode transitions: {current_node.get('transitions', {})}")
    
    # Let's manually check the matching logic for motivation
    user_input_lower = test_response.lower().strip()
    print(f"\nUser input lower: '{user_input_lower}'")
    
    # These are the motivation indicators from the implementation
    motivation_indicators = ["freedom", "tired of my job", "need more income", "for my family",
                           "want to change", "looking for opportunity", "ready for something new"]
    
    print("Checking motivation indicators:")
    for indicator in motivation_indicators:
        match = indicator in user_input_lower
        print(f"  '{indicator}' in '{user_input_lower}': {match}")
        
        if match:
            print(f"    Found match for '{indicator}'!")
            
    # Let's manually check the matching logic for callback
    callback_input_lower = callback_response.lower().strip()
    print(f"\nCallback input lower: '{callback_input_lower}'")
    
    # These are the callback indicators from the implementation
    callback_indicators = ["have to go", "busy", "call me back", "need to end", "got to run"]
    
    print("Checking callback indicators:")
    for indicator in callback_indicators:
        match = indicator in callback_input_lower
        print(f"  '{indicator}' in '{callback_input_lower}': {match}")
        
        if match:
            print(f"    Found match for '{indicator}'!")

if __name__ == "__main__":
    debug_why_now_transition()