#!/usr/bin/env python3
"""
Test script for the N_KB_Q&A_With_StrategicNarrative_V3_Adaptive node.
"""

import pytest
import os
import sys
import logging
from unittest.mock import MagicMock, patch, AsyncMock # Import AsyncMock

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from caller_agent import CallFlowAgent, CallFlowState
from generative_objection_handler import ResponseOrchestrator

@pytest.mark.asyncio
async def test_kb_node():
    """
    Test the N_KB_Q&A_With_StrategicNarrative_V3_Adaptive node functionality.
    """
    try:
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Check if OpenAI API key is available
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            print("WARNING: OPENAI_API_KEY environment variable not set.")
            print("The KB processor will use fallback responses.")
            print("To test full KB functionality, please set the OPENAI_API_KEY environment variable.")
            print()
        
        # Initialize the call flow agent
        print("Initializing CallFlowAgent...")
        # Mock the ResponseOrchestrator and its generate_response method
        with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
             patch('caller_agent.nodes') as MockNodes: # Patch nodes
            mock_orchestrator_instance = MockResponseOrchestrator.return_value
            expected_orchestrator_responses = [ # Store expected responses in a list
                {'response': "The benefits include passive income and flexibility.", 'should_transition': False, 'retry_goal': True},
                {'response': "You can potentially make $20,000 a month.", 'should_transition': False, 'retry_goal': True},
                {'response': "Rank and Bank is a strategy for digital real estate.", 'should_transition': False, 'retry_goal': True},
                {'response': "The digital real estate model involves building and ranking websites.", 'should_transition': False, 'retry_goal': True},
            ]
            mock_orchestrator_instance.generate_response.side_effect = expected_orchestrator_responses # Assign the list to side_effect

            # Configure MockNodes to return a simplified node definition
            MockNodes.get.return_value = {
                'id': 'N_KB_Q&A_With_StrategicNarrative_V3_Adaptive',
                'goal': '', # Ensure goal is empty for this test
                'transitions': {'default': 'N200_Super_WorkAndIncomeBackground_V3_Adaptive'},
                'transition_conditions': {}
            }

            # Initialize the call flow agent
            print("Initializing CallFlowAgent...")
            agent = CallFlowAgent()
            
            # Mock the session and its userdata
            mock_session = MagicMock()
            agent.session = mock_session
            agent.session.userdata = CallFlowState(
                customer_name="John Doe",
                current_node_id="N_KB_Q&A_With_StrategicNarrative_V3_Adaptive", # Set current_node_id
                personality_type="DIRECT",
                user_preferences={
                    "interests": ["business opportunities", "income generation"],
                    "income_level": 50000
                },
                conversation_history=[
                    {"speaker": "user", "text": "I'm interested in learning about business opportunities."},
                    {"speaker": "agent", "text": "I'd be happy to help you learn about business opportunities."},
                    {"speaker": "user", "text": "I want to know more about how to generate additional income."}
                ]
            )
            # Mock _safe_say to prevent actual speaking during test
            agent._safe_say = AsyncMock(return_value=True) # Use AsyncMock
            # Mock _transition_to_node as it might be called
            agent._transition_to_node = AsyncMock(return_value=None) # Use AsyncMock
            # Mock _enforce_final_turn_compliance to return text as is
            agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)

            # Test queries for the KB node
            test_queries = [
                "What are the benefits of this business model?",
                "How much money can I make with this program?",
                "What is the Rank and Bank strategy?",
                "How does the digital real estate model work?"
            ]
            
            print("\nTesting N_KB_Q&A_With_StrategicNarrative_V3_Adaptive node:")
            for i, query in enumerate(test_queries, 1):
                print(f"\n{i}. Query: {query}")
                
                # Simulate the KB node processing by calling _handle_user_response
                # This will internally call response_orchestrator.generate_response
                await agent._handle_user_response(query, agent.session.userdata)
                
                # Assert that generate_response was called with the correct query
                mock_orchestrator_instance.generate_response.assert_any_call(
                    query,
                    {'id': 'N_KB_Q&A_With_StrategicNarrative_V3_Adaptive', 'goal': '', 'transitions': {'default': 'N200_Super_WorkAndIncomeBackground_V3_Adaptive'}, 'transition_conditions': {}}
                )
                
                # Assert that _safe_say was called with the mocked response
                expected_response = expected_orchestrator_responses[i-1]['response'] # Access from the stored list
                agent._safe_say.assert_any_call(expected_response, agent.session.userdata, mark_spoken=False)
                
                print(f"   Response (mocked): {expected_response}")
                
            print("\nTest completed successfully!")
            
    except Exception as e:
        logging.error(f"Error testing KB node: {e}", exc_info=True)
        # Do not exit, let pytest handle the failure
        raise # Re-raise the exception to mark the test as failed

if __name__ == "__main__":
    test_kb_node()