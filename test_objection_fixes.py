#!/usr/bin/env python3
"""
Test script to verify objection handling fixes.
Tests that the system properly answers business model questions
instead of giving generic responses.
"""

import asyncio
import pytest
import logging
from unittest.mock import MagicMock, AsyncMock, patch
from caller_agent import CallFlowAgent, CallFlowState
from conversation_state_manager import ConversationStateManager
from generative_objection_handler import ResponseOrchestrator
from kb_processor import KBProcessor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_business_model_question():
    """Test that business model questions get proper answers."""
    print("\n" + "="*60)
    print("TEST: Business Model Question Handling")
    print("="*60)
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Our business model involves ranking websites for local services like plumbing and HVAC.",
            'should_transition': False,
            'retry_goal': True,
            'identified_objection': None,
            'selected_strategy': None
        }

        MockNodes.get.return_value = {
            'id': '001_N_Opener',
            'goal': '',
            'transitions': {'default': 'N200_Super_WorkAndIncomeBackground_V3_Adaptive'},
            'transition_conditions': {}
        }

        # Initialize agent
        agent = CallFlowAgent()
        
        # Mock session and userdata
        mock_session = MagicMock()
        agent.session = mock_session
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="001_N_Opener",
            conversation_history=[
                {"speaker": "user", "text": "Hello"},
                {"speaker": "agent", "text": "Hi there!"}
            ]
        )
        
        # Mock internal methods
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test business model question
        user_utterance = "How does your business model work exactly?"
        print(f"\nUser: {user_utterance}")
        
        # Process the utterance
        await agent._handle_user_response(user_utterance, agent.session.userdata)
        
        # Assertions
        mock_orchestrator_instance.generate_response.assert_called_once()
        call_args, _ = mock_orchestrator_instance.generate_response.call_args
        assert call_args[0] == user_utterance
        assert call_args[1]['id'] == '001_N_Opener'

        
        spoken_text = agent._safe_say.call_args[0][0]
        print(f"\nAgent Response: {spoken_text}")
        
        assert any(keyword in spoken_text.lower() for keyword in
               ['rank websites', 'local services', 'plumbing', 'hvac', 'seo']), \
               "Response is generic, missing business model details"
        
        # Check if _transition_to_node was NOT called (since should_transition is False)
        agent._transition_to_node.assert_not_called()

@pytest.mark.asyncio
async def test_pricing_question():
    """Test that pricing questions get proper answers."""
    print("\n" + "="*60)
    print("TEST: Pricing Question Handling")
    print("="*60)
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        # Simulate a pricing-related response
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "We don't have a fixed price; it depends on the project scope, but we offer a free consultation.",
            'should_transition': False,
            'retry_goal': True,
            'identified_objection': None,
            'selected_strategy': None
        }

        MockNodes.get.return_value = {
            'id': '001_N_Opener',
            'goal': '',
            'transitions': {'default': 'N200_Super_WorkAndIncomeBackground_V3_Adaptive'},
            'transition_conditions': {}
        }

        # Initialize agent
        agent = CallFlowAgent()
        
        # Mock session and userdata
        mock_session = MagicMock()
        agent.session = mock_session
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="001_N_Opener",
            conversation_history=[
                {"speaker": "user", "text": "Hello"},
                {"speaker": "agent", "text": "Hi there!"}
            ]
        )
        
        # Mock internal methods
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test pricing question
        user_utterance = "What is your pricing?"
        print(f"\nUser: {user_utterance}")
        
        # Process the utterance
        await agent._handle_user_response(user_utterance, agent.session.userdata)
        
        # Assertions
        mock_orchestrator_instance.generate_response.assert_called_once()
        call_args, _ = mock_orchestrator_instance.generate_response.call_args
        assert call_args[0] == user_utterance
        assert call_args[1]['id'] == '001_N_Opener'
        
        spoken_text = agent._safe_say.call_args[0][0]
        print(f"\nAgent Response: {spoken_text}")
        
        assert any(keyword in spoken_text.lower() for keyword in
               ['price', 'pricing', 'consultation', 'scope']), \
               "Response is generic, missing pricing details"
        
        # Check if _transition_to_node was NOT called
        agent._transition_to_node.assert_not_called()

# Example of a main block for running tests if not using pytest
if __name__ == '__main__':
    async def run_tests():
        await test_business_model_question()
        await test_pricing_question()
    asyncio.run(run_tests())