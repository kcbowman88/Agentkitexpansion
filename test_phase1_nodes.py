#!/usr/bin/env python3
"""
Test script for verifying the content-based transition logic implementation for Phase 1 untested nodes.
"""

import sys
import os
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# Add the current directory to the path so we can import caller_agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from caller_agent import CallFlowAgent, CallFlowState
from conversation_state_manager import ConversationStateManager


@pytest.mark.asyncio
async def test_intro_help_request_transitions():
    """Test the N001B_IntroAndHelpRequest_Only node transitions."""
    print("Testing N001B_IntroAndHelpRequest_Only transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Sure, what can I help you with?",
            'should_transition': True,
            'target_node': "N200_Super_WorkAndIncomeBackground_V3_Adaptive",
            'retry_goal': False,
            'identified_objection': None,
            'selected_strategy': None
        }

        MockNodes.get.return_value = {
            'id': 'N001B_IntroAndHelpRequest_Only',
            'goal': 'help request',
            'transitions': {'default': 'N200_Super_WorkAndIncomeBackground_V3_Adaptive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N001B_IntroAndHelpRequest_Only",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        help_request_responses = [
            "Sure, what can I help you with?",
            "Okay...",
            "What is this about?",
            "Yes?",
            "Hmm?",
            "I'm listening"
        ]
        
        for response in help_request_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N001B_IntroAndHelpRequest_Only', 'goal': 'help request', 'transitions': {'default': 'N200_Super_WorkAndIncomeBackground_V3_Adaptive'}, 'transition_conditions': {}}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N200_Super_WorkAndIncomeBackground_V3_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N001B_IntroAndHelpRequest_Only transition tests passed!\n")


@pytest.mark.asyncio
async def test_introduce_model_transitions():
    """Test the N_IntroduceModel_And_AskQuestions_V3_Adaptive node transitions."""
    print("Testing N_IntroduceModel_And_AskQuestions_V3_Adaptive transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "We help local businesses rank higher on Google. What questions come to mind?",
            'should_transition': True,
            'target_node': "N_KB_Q&A_With_StrategicNarrative_V3_Adaptive", # Example transition
            'retry_goal': False,
            'identified_objection': None,
            'selected_strategy': None
        }

        MockNodes.get.return_value = {
            'id': 'N_IntroduceModel_And_AskQuestions_V3_Adaptive',
            'goal': 'introduce model',
            'transitions': {'default': 'N_KB_Q&A_With_StrategicNarrative_V3_Adaptive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_IntroduceModel_And_AskQuestions_V3_Adaptive",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        question_responses = [
            "How does that work?",
            "What kind of websites?",
            "Sounds too good to be true.",
            "Can you explain more?",
            "I'm interested"
        ]
        
        for response in question_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_IntroduceModel_And_AskQuestions_V3_Adaptive', 'goal': 'introduce model', 'transitions': {'default': 'N_KB_Q&A_With_StrategicNarrative_V3_Adaptive'}, 'transition_conditions': {}}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_KB_Q&A_With_StrategicNarrative_V3_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_IntroduceModel_And_AskQuestions_V3_Adaptive transition tests passed!\n")


@pytest.mark.asyncio
async def test_deframe_initial_objection_transitions():
    """Test the N003B_DeframeInitialObjection_V7_GoalOriented node transitions."""
    print("Testing N003B_DeframeInitialObjection_V7_GoalOriented transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        
        # Mock for curiosity expressed responses
        mock_orchestrator_instance.generate_response.side_effect = [
            {
                'response': "I understand your skepticism. Many people are curious about how this works. Would you like me to explain further?",
                'should_transition': True,
                'target_node': "N_KB_Q&A_With_StrategicNarrative_V3_Adaptive",
                'retry_goal': False,
                'identified_objection': "curiosity_expressed",
                'selected_strategy': "deframe"
            } for _ in range(7) # For each curiosity response
        ] + [
            # Mock for callback requested responses
            {
                'response': "I understand you're busy. Can I schedule a brief call for later?",
                'should_transition': True,
                'target_node': "N_Obj_RealBusy_OfferReschedule",
                'retry_goal': False,
                'identified_objection': "callback_requested",
                'selected_strategy': "reschedule"
            } for _ in range(5) # For each callback response
        ]

        MockNodes.get.return_value = {
            'id': 'N003B_DeframeInitialObjection_V7_GoalOriented',
            'goal': 'deframe objection',
            'transitions': {
                'curiosity_expressed': 'N_KB_Q&A_With_StrategicNarrative_V3_Adaptive',
                'callback_requested': 'N_Obj_RealBusy_OfferReschedule',
                'default': 'N200_Super_WorkAndIncomeBackground_V3_Adaptive'
            },
            'transition_conditions': {
                'curiosity_expressed': ['tell me more', 'how does it work', 'yes', 'maybe', 'if it works', 'i\'m curious', 'explore'],
                'callback_requested': ['call me back', 'have to go', 'busy', 'can you call me back later', 'i have to go now', 'call back', 'have to go', 'busy']
            }
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N003B_DeframeInitialObjection_V7_GoalOriented",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test curiosity expressed responses
        curiosity_responses = [
            "Okay, tell me more.",
            "How does it work?",
            "Yes",
            "Maybe",
            "If it works",
            "I'm curious",
            "Explore"
        ]
        
        for response in curiosity_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N003B_DeframeInitialObjection_V7_GoalOriented', 'goal': 'deframe objection', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_KB_Q&A_With_StrategicNarrative_V3_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (curiosity) handled correctly.")
        
        # Test callback requested responses
        callback_responses = [
            "Can you call me back later?",
            "I have to go now.",
            "Call back",
            "Have to go",
            "Busy"
        ]
        
        for response in callback_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N003B_DeframeInitialObjection_V7_GoalOriented', 'goal': 'deframe objection', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Obj_RealBusy_OfferReschedule", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (callback) handled correctly.")
    
    print("All N003B_DeframeInitialObjection_V7_GoalOriented transition tests passed!\n")


@pytest.mark.asyncio
async def test_early_dismiss_share_background_transitions():
    """Test the N_Obj_EarlyDismiss_ShareBackground_DeliverStoryHook_V3_FullyTuned node transitions."""
    print("Testing N_Obj_EarlyDismiss_ShareBackground_DeliverStoryHook_V3_FullyTuned transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "I understand you're curious about why I called. We help local businesses rank higher on Google. Does that make sense?",
            'should_transition': True,
            'target_node': "N_IntroduceModel_And_AskQuestions_V3_Adaptive",
            'retry_goal': False,
            'identified_objection': "responded_to_why_question",
            'selected_strategy': "share_background"
        }

        MockNodes.get.return_value = {
            'id': 'N_Obj_EarlyDismiss_ShareBackground_DeliverStoryHook_V3_FullyTuned',
            'goal': 'share background',
            'transitions': {'default': 'N_IntroduceModel_And_AskQuestions_V3_Adaptive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Obj_EarlyDismiss_ShareBackground_DeliverStoryHook_V3_FullyTuned",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        why_question_responses = [
            "Why?",
            "No, I don't know.",
            "Because of Google?",
            "I'm not sure",
            "That's interesting"
        ]
        
        for response in why_question_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_EarlyDismiss_ShareBackground_DeliverStoryHook_V3_FullyTuned', 'goal': 'share background', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_IntroduceModel_And_AskQuestions_V3_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Obj_EarlyDismiss_ShareBackground_DeliverStoryHook_V3_FullyTuned transition tests passed!\n")
