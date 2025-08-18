#!/usr/bin/env python3
"""
Debug script to test D-path rotation for IntroduceModel objections
"""
import sys
import os
from unittest.mock import Mock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from caller_agent import CallFlowAgent, CallFlowState
from objection_handler import Objection, ObjectionType, FLAGS

def debug_d_rotation():
    """
    Debug the D-path rotation issue
    """
    # Enable A2 engine for IntroduceModel node with D persona
    FLAGS['engine_global'] = True
    FLAGS['nodes']['IntroduceModel']['D'] = True
    FLAGS['ab_guard']['percent'] = 100
    
    # Initialize the call flow agent
    print("Initializing CallFlowAgent...")
    agent = CallFlowAgent()
    
    # Create a mock session
    agent.session = Mock()
    agent.session.userdata = CallFlowState()
    agent.session.userdata.current_node_id = "N_IntroduceModel_And_AskQuestions_V3_Adaptive_Dominant"
    agent.session.userdata.customer_name = "John"
    agent.session.userdata.personality_type = "D"
    agent.session.userdata.emotional_state = "neutral"
    
    # Test D-variant rotation for IntroduceModel skepticism
    print("\nTesting D-variant rotation for IntroduceModel skepticism:")
    objection_text = "Sounds like a scam. Show me proof it's legit."
    # Simple sentiment analysis
    sentiment_score = 0.0  # Neutral sentiment
    categorized_type = agent.objection_handler.categorize_objection(objection_text, sentiment_score)
    
    print(f"Objection type: {categorized_type}")
    print(f"Sentiment score: {sentiment_score}")
    
    resp_list = []
    for i in range(3):
        print(f"\n--- Call {i+1} ---")
        objection = Objection(type=categorized_type, content=objection_text, timestamp=0.0)
        response, _ = agent.objection_handler.handle_objection(
            objection, agent.session.userdata.personality_type, agent.session.userdata.emotional_state, agent.session.userdata.current_node_id
        )
        resp_list.append(response)
        print(f"Response: {response}")
    
    # Check if responses are distinct
    unique_responses = set(resp_list)
    print(f"\nNumber of unique responses: {len(unique_responses)}")
    print(f"Responses: {resp_list}")
    
    if len(unique_responses) >= 3:
        print("✓ D-path rotates variations correctly")
    else:
        print("✗ D-path does not rotate variations correctly")

if __name__ == "__main__":
    debug_d_rotation()