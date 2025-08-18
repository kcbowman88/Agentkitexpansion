#!/usr/bin/env python3
"""
Debug script to simulate the Name Confirmation transition logic
and see exactly what transition key is being returned.
"""

import sys
import os
import logging

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Import the necessary modules
from caller_agent import CallFlowAgent
from call_flow import nodes

def simulate_transition(user_input="Yeah."):
    """
    Simulate the content-based transition for the N001A_NameConfirmation_Only node
    with the given user input.
    """
    print(f"=== Debugging Name Confirmation Transition ===")
    print(f"User input: '{user_input}'")
    
    # Create an instance of CallFlowAgent
    agent = CallFlowAgent()
    
    # Get the node definition
    node_id = "N001A_NameConfirmation_Only"
    current_node = nodes.get(node_id)
    
    if not current_node:
        print(f"ERROR: Node '{node_id}' not found in call_flow.")
        return
    
    print(f"Node ID: {node_id}")
    print(f"Available transitions: {list(current_node.get('transitions', {}).keys())}")
    
    # Check what the content-based transition logic returns
    content_transition = agent._get_content_based_transition(node_id, user_input)
    print(f"Content-based transition result: {content_transition}")
    
    # Check if the transition exists in the node's transitions
    if content_transition:
        if content_transition in current_node.get('transitions', {}):
            next_node_id = current_node['transitions'][content_transition]
            print(f"Transition '{content_transition}' maps to node: {next_node_id}")
            
            # Check if the target node exists
            target_node = nodes.get(next_node_id)
            if target_node:
                print(f"Target node '{next_node_id}' exists.")
            else:
                print(f"ERROR: Target node '{next_node_id}' does not exist!")
        else:
            print(f"ERROR: Transition '{content_transition}' not found in node transitions!")
    else:
        print("No content-based transition found.")
        
        # Check what the default transition would be
        if 'default' in current_node.get('transitions', {}):
            default_transition = 'default'
            next_node_id = current_node['transitions'][default_transition]
            print(f"Default transition would be '{default_transition}' to node: {next_node_id}")
        else:
            print("No default transition found either!")
    
    # Let's also check what the _handle_user_response method would do
    print("\n=== Analyzing transition priority logic ===")
    
    # Simulate the priority logic from _handle_user_response
    # 1. Content-based transition (highest priority)
    content_transition = agent._get_content_based_transition(node_id, user_input)
    print(f"1. Content-based transition: {content_transition}")
    
    # 2. Context-based transition (second priority)
    context_transition = None
    print(f"2. Context-based transition: {context_transition}")
    
    # 3. Personality-based transition (third priority)
    personality_transition = None
    print(f"3. Personality-based transition: {personality_transition}")
    
    # 4. Default transition (lowest priority)
    default_transition = current_node.get('transitions', {}).get('default')
    print(f"4. Default transition: {default_transition}")
    
    # Determine which transition would be used
    if content_transition:
        chosen_transition = content_transition
        reason = "content-based"
    elif context_transition:
        chosen_transition = context_transition
        reason = "context-based"
    elif personality_transition:
        chosen_transition = personality_transition
        reason = "personality-based"
    elif default_transition:
        chosen_transition = 'default'
        reason = "default"
    else:
        chosen_transition = None
        reason = "none"
    
    print(f"\n=== Final Decision ===")
    print(f"Chosen transition: {chosen_transition} ({reason})")
    
    if chosen_transition and chosen_transition in current_node.get('transitions', {}):
        next_node_id = current_node['transitions'][chosen_transition]
        print(f"This would transition to node: {next_node_id}")
        
        # Check if target node exists
        target_node = nodes.get(next_node_id)
        if target_node:
            print(f"Target node exists: {next_node_id}")
        else:
            print(f"ERROR: Target node '{next_node_id}' does not exist!")
    else:
        print("No valid transition found!")

def test_wrong_number_detection():
    """
    Test the wrong number detection logic specifically
    """
    print("\n=== Testing Wrong Number Detection ===")
    
    agent = CallFlowAgent()
    node_id = "N001A_NameConfirmation_Only"
    
    # Test cases for wrong number responses
    wrong_number_inputs = [
        "wrong number",
        "Not here",
        "No John here",
        "You have the wrong person",
        "He doesn't live here"
    ]
    
    for test_input in wrong_number_inputs:
        result = agent._get_content_based_transition(node_id, test_input)
        print(f"Input: '{test_input}' -> Transition: {result}")
    
    # Test cases for name confirmation responses
    name_confirmation_inputs = [
        "yes",
        "speaking",
        "this is he",
        "this is she",
        "uh-huh",
        "okay",
        "who is this",
        "what is this regarding",
        "yeah"
    ]
    
    print("\n=== Testing Name Confirmation Detection ===")
    for test_input in name_confirmation_inputs:
        result = agent._get_content_based_transition(node_id, test_input)
        print(f"Input: '{test_input}' -> Transition: {result}")

if __name__ == "__main__":
    # Test with the specific input from the logs
    simulate_transition("Yeah.")
    
    # Also test the wrong number detection
    test_wrong_number_detection()