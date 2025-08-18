import pytest # Added for pytest.mark.asyncio
import sys
import os
import logging
from unittest.mock import MagicMock, patch, AsyncMock # Import AsyncMock

# Add the current directory to the path so we can import caller_agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from caller_agent import CallFlowAgent, CallFlowState
from generative_objection_handler import ResponseOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)

import asyncio

@pytest.mark.asyncio
async def test_kb_node_without_income():
    """Test the KB Q&A node without income data"""
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Based on what I've learned, many of our students have been able to generate significant income. That's a great question, John!",
            'should_transition': False,
            'retry_goal': True,
            'identified_objection': None,
            'selected_strategy': None
        }

        agent = CallFlowAgent()
        mock_session = MagicMock()
        agent.session = mock_session
        agent.session.userdata = CallFlowState(
            customer_name="John",
            current_node_id="N_KB_Q&A_With_StrategicNarrative_V3_Adaptive",
            personality_type="I",
            user_preferences={
                "interests": ["passive income", "website"]
            },
        )
        agent._safe_say = AsyncMock(return_value=True) # Use AsyncMock
        agent._transition_to_node = AsyncMock(return_value=None) # Use AsyncMock

        user_query = "How much money can I make?"
        await agent._handle_user_response(user_query, agent.session.userdata)
        
        mock_orchestrator_instance.generate_response.assert_called_once()
        agent._safe_say.assert_called_once()
        
        spoken_text = agent._safe_say.call_args[0][0]
        assert "many of our students have been able to generate significant income" in spoken_text
        assert "Based on what I've learned" in spoken_text
        assert "That's a great question, John!" in spoken_text
        print("\nSUCCESS: test_kb_node_without_income passed.")

@pytest.mark.asyncio
async def test_kb_node_with_income():
    """Test the KB Q&A node with income data"""
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Building on your current income of $75,000, our program can help you grow. That's a great question, John!",
            'should_transition': False,
            'retry_goal': True,
            'identified_objection': None,
            'selected_strategy': None
        }

        agent = CallFlowAgent()
        mock_session = MagicMock()
        agent.session = mock_session
        agent.session.userdata = CallFlowState(
            customer_name="John",
            current_node_id="N_KB_Q&A_With_StrategicNarrative_V3_Adaptive",
            personality_type="I",
            user_preferences={
                "interests": ["passive income", "website"],
                "employment_status": "employed",
                "income_level": 75000
            },
        )
        agent._safe_say = AsyncMock(return_value=True) # Use AsyncMock
        agent._transition_to_node = AsyncMock(return_value=None) # Use AsyncMock

        user_query = "How much money can I make?"
        await agent._handle_user_response(user_query, agent.session.userdata)
        
        mock_orchestrator_instance.generate_response.assert_called_once()
        agent._safe_say.assert_called_once()
        
        spoken_text = agent._safe_say.call_args[0][0]
        assert "Building on your current income of $75,000" in spoken_text
        assert "That's a great question, John!" in spoken_text
        print("\nSUCCESS: test_kb_node_with_income passed.")

if __name__ == "__main__":
    test_kb_node_without_income()
    test_kb_node_with_income()