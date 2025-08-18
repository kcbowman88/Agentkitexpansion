#!/usr/bin/env python3
"""
Debug script to simulate the exact transition issue.
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

def simulate_transition_issue(user_input="Yeah."):
    """
    Simulate the exact issue where the transition logic incorrectly passes
    the transition key instead of the target node ID to _transition_to_node.
    """
    print(f"=== Simulating Transition Issue ===")
    print(f"User input: '{user_input}'")
    
    # Create an instance of CallFlowAgent
    agent = CallFlowAgent()
    
    # Get the current node (N001A_NameConfirmation_Only)
    current_node_id = "N001A_NameConfirmation_Only"
    current_node = nodes.get(current_node_id)
    
    if not current_node:
        print(f"ERROR: Node '{current_node_id}' not found in call_flow.")
        return
    
    print(f"Current node: {current_node_id}")
    print(f"Available transitions: {current_node.get('transitions', {})}")
    
    # Simulate what happens in _handle_user_response method
    print("\n=== Simulating _handle_user_response logic ===")
    
    # 1. Get content-based transition
    content_transition = agent._get_content_based_transition(current_node_id, user_input)
    print(f"Content-based transition key: {content_transition}")
    
    # 2. Simulate the problematic logic in _handle_user_response
    # This is the bug - we're passing the transition key instead of the target node ID
    if content_transition:
        # BUG: This is passing the transition key instead of the target node ID
        next_node_id = content_transition  # This is "default" instead of the actual node ID
        print(f"BUG: Passing transition key '{next_node_id}' to _transition_to_node")
        
        # Check if this "node" exists
        target_node = nodes.get(next_node_id)
        if target_node:
            print(f"Target node '{next_node_id}' exists.")
        else:
            print(f"ERROR: Target 'node' '{next_node_id}' does not exist!")
            
        # What should happen instead
        if content_transition in current_node.get('transitions', {}):
            correct_next_node_id = current_node['transitions'][content_transition]
            print(f"CORRECT: Should pass node ID '{correct_next_node_id}' to _transition_to_node")
            
            # Check if the correct target node exists
            correct_target_node = nodes.get(correct_next_node_id)
            if correct_target_node:
                print(f"Correct target node '{correct_next_node_id}' exists.")
            else:
                print(f"ERROR: Correct target node '{correct_next_node_id}' does not exist!")
    
    # 3. Show what _transition_to_node would do with the incorrect parameter
    print("\n=== What _transition_to_node does with incorrect parameter ===")
    # This would try to find a node with ID "default", which doesn't exist
    print(f"_transition_to_node would try to find node with ID: '{content_transition}'")
    print(f"Result: Node not found error")

if __name__ == "__main__":
    # Test with the specific input from the logs
    simulate_transition_issue("Yeah.")
    
    print("\n" + "="*50)
    
    # Also test with a wrong number input
    print("\n=== Testing with wrong number input ===")
    simulate_transition_issue("wrong number")