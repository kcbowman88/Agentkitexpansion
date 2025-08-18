#!/usr/bin/env python3
"""
Test script for verifying the content-based transition logic implementation for Phase 5 untested nodes.
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
async def test_video_assign_gentle_intro_transitions():
    """Test the N_Video_Assign_GentleIntro_V3_FullyTuned node transitions."""
    print("Testing N_Video_Assign_GentleIntro_V3_FullyTuned transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Great! Let's get started.",
            'should_transition': True,
            'target_node': "N_Video_ReinforceValue_FeeContext_V3_FullyTuned",
            'retry_goal': False,
            'identified_objection': "agrees",
            'selected_strategy': "confirm_video_assignment"
        }

        MockNodes.get.return_value = {
            'id': 'N_Video_Assign_GentleIntro_V3_FullyTuned',
            'goal': 'assign gentle intro',
            'transitions': {'default': 'N_Video_ReinforceValue_FeeContext_V3_FullyTuned'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Video_Assign_GentleIntro_V3_FullyTuned",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        accepted_responses = [
            "Sure, I can do that.",
            "Makes sense.",
            "Yes",
            "Sure",
            "Okay",
            "Makes sense"
        ]
        
        for response in accepted_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Video_Assign_GentleIntro_V3_FullyTuned', 'goal': 'assign gentle intro', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Video_ReinforceValue_FeeContext_V3_FullyTuned", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Video_Assign_GentleIntro_V3_FullyTuned transition tests passed!\n")


@pytest.mark.asyncio
async def test_video_reinforce_value_transitions():
    """Test the N_Video_ReinforceValue_FeeContext_V3_FullyTuned node transitions."""
    print("Testing N_Video_ReinforceValue_FeeContext_V3_FullyTuned transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Great! Let's move on to the next step.",
            'should_transition': True,
            'target_node': "N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint",
            'retry_goal': False,
            'identified_objection': "value_acknowledged",
            'selected_strategy': "reinforce_value"
        }

        MockNodes.get.return_value = {
            'id': 'N_Video_ReinforceValue_FeeContext_V3_FullyTuned',
            'goal': 'reinforce value',
            'transitions': {'default': 'N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Video_ReinforceValue_FeeContext_V3_FullyTuned",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        acknowledged_responses = [
            "Okay, sounds good.",
            "All good on that front.",
            "Yes",
            "Okay",
            "Sounds good",
            "All good"
        ]
        
        for response in acknowledged_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Video_ReinforceValue_FeeContext_V3_FullyTuned', 'goal': 'reinforce value', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Video_ReinforceValue_FeeContext_V3_FullyTuned transition tests passed!\n")


@pytest.mark.asyncio
async def test_video_social_proof_transitions():
    """Test the N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint node transitions."""
    print("Testing N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Great! Let's move on to the next step.",
            'should_transition': True,
            'target_node': "N_Video_AssignAndCommit_V1_FullyTuned",
            'retry_goal': False,
            'identified_objection': "logic_acknowledged",
            'selected_strategy': "social_proof"
        }

        MockNodes.get.return_value = {
            'id': 'N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint',
            'goal': 'social proof',
            'transitions': {'default': 'N_Video_AssignAndCommit_V1_FullyTuned'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        acknowledged_responses = [
            "Yeah, I get it.",
            "Okay.",
            "Yeah",
            "I get it",
            "Okay",
            "You know"
        ]
        
        for response in acknowledged_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint', 'goal': 'social proof', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Video_AssignAndCommit_V1_FullyTuned", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint transition tests passed!\n")


@pytest.mark.asyncio
async def test_video_assign_and_commit_transitions():
    """Test the N_Video_AssignAndCommit_V1_FullyTuned node transitions."""
    print("Testing N_Video_AssignAndCommit_V1_FullyTuned transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Great! I'll send you the link. Let's move on.",
            'should_transition': True,
            'target_node': "N_Video_ConfirmAndReply_V1_Adaptive",
            'retry_goal': False,
            'identified_objection': "commits",
            'selected_strategy': "assign_and_commit"
        }

        MockNodes.get.return_value = {
            'id': 'N_Video_AssignAndCommit_V1_FullyTuned',
            'goal': 'assign and commit',
            'transitions': {'default': 'N_Video_ConfirmAndReply_V1_Adaptive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Video_AssignAndCommit_V1_FullyTuned",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        committed_responses = [
            "Yes, I can watch it now.",
            "That works perfectly.",
            "Yes",
            "I can",
            "That works"
        ]
        
        for response in committed_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Video_AssignAndCommit_V1_FullyTuned', 'goal': 'assign and commit', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Video_ConfirmAndReply_V1_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Video_AssignAndCommit_V1_FullyTuned transition tests passed!\n")


@pytest.mark.asyncio
async def test_video_confirm_and_reply_transitions():
    """Test the N_Video_ConfirmAndReply_V1_Adaptive node transitions."""
    print("Testing N_Video_ConfirmAndReply_V1_Adaptive transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Great! Let's move on to the next step.",
            'should_transition': True,
            'target_node': "N_AskAboutReminderSetup_V1_Adaptive",
            'retry_goal': False,
            'identified_objection': "replied_to_text",
            'selected_strategy': "confirm_reply"
        }

        MockNodes.get.return_value = {
            'id': 'N_Video_ConfirmAndReply_V1_Adaptive',
            'goal': 'confirm and reply',
            'transitions': {'default': 'N_AskAboutReminderSetup_V1_Adaptive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Video_ConfirmAndReply_V1_Adaptive",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        replied_responses = [
            "I just replied.",
            "Sent.",
            "I replied",
            "Sent",
            "Got it",
            "Done",
            "Replied"
        ]
        
        for response in replied_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Video_ConfirmAndReply_V1_Adaptive', 'goal': 'confirm and reply', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_AskAboutReminderSetup_V1_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Video_ConfirmAndReply_V1_Adaptive transition tests passed!\n")


@pytest.mark.asyncio
async def test_ask_about_reminder_setup_transitions():
    """Test the N_AskAboutReminderSetup_V1_Adaptive node transitions."""
    print("Testing N_AskAboutReminderSetup_V1_Adaptive transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        
        # Mock for knows how responses
        mock_orchestrator_instance.generate_response.side_effect = [
            {
                'response': "Great! Let's move on to the next step.",
                'should_transition': True,
                'target_node': "N_CheckForTextReceipt_V1_Adaptive",
                'retry_goal': False,
                'identified_objection': "knows_how",
                'selected_strategy': "confirm_reminder_setup"
            } for _ in range(3) # For each knows how response
        ] + [
            # Mock for needs help responses
            {
                'response': "Okay, I can help you with that. Let's move on.",
                'should_transition': True,
                'target_node': "N_CheckForTextReceipt_V1_Adaptive",
                'retry_goal': False,
                'identified_objection': "needs_help",
                'selected_strategy': "assist_reminder_setup"
            } for _ in range(3) # For each needs help response
        ]

        MockNodes.get.return_value = {
            'id': 'N_AskAboutReminderSetup_V1_Adaptive',
            'goal': 'ask about reminder setup',
            'transitions': {
                'knows_how': 'N_CheckForTextReceipt_V1_Adaptive',
                'needs_help': 'N_CheckForTextReceipt_V1_Adaptive',
                'default': 'N_EndCall_Final_V2_Decisive'
            },
            'transition_conditions': {
                'knows_how': ['yes', 'i do', 'sure'],
                'needs_help': ['no', 'i don\'t', 'not sure']
            }
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_AskAboutReminderSetup_V1_Adaptive",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test knows how responses
        knows_how_responses = [
            "Yes",
            "I do",
            "Sure"
        ]
        
        for response in knows_how_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_AskAboutReminderSetup_V1_Adaptive', 'goal': 'ask about reminder setup', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_CheckForTextReceipt_V1_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (knows how) handled correctly.")
        
        # Test needs help responses
        needs_help_responses = [
            "No",
            "I don't",
            "Not sure"
        ]
        
        for response in needs_help_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_AskAboutReminderSetup_V1_Adaptive', 'goal': 'ask about reminder setup', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_CheckForTextReceipt_V1_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (needs help) handled correctly.")
    
    print("All N_AskAboutReminderSetup_V1_Adaptive transition tests passed!\n")


@pytest.mark.asyncio
async def test_check_text_receipt_transitions():
    """Test the N_CheckForTextReceipt_V1_Adaptive node transitions."""
    print("Testing N_CheckForTextReceipt_V1_Adaptive transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Great! Let's move on to the next step.",
            'should_transition': True,
            'target_node': "N_ConfirmAndRequestReply_V4_PatientListener",
            'retry_goal': False,
            'identified_objection': "received",
            'selected_strategy': "confirm_receipt"
        }

        MockNodes.get.return_value = {
            'id': 'N_CheckForTextReceipt_V1_Adaptive',
            'goal': 'check text receipt',
            'transitions': {'default': 'N_ConfirmAndRequestReply_V4_PatientListener'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_CheckForTextReceipt_V1_Adaptive",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        received_responses = [
            "Yes, I just got it.",
            "Yes",
            "I got it",
            "It came through"
        ]
        
        for response in received_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_CheckForTextReceipt_V1_Adaptive', 'goal': 'check text receipt', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_ConfirmAndRequestReply_V4_PatientListener", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_CheckForTextReceipt_V1_Adaptive transition tests passed!\n")


@pytest.mark.asyncio
async def test_confirm_and_request_reply_transitions():
    """Test the N_ConfirmAndRequestReply_V4_PatientListener node transitions."""
    print("Testing N_ConfirmAndRequestReply_V4_PatientListener transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Great! Let's move on to the next step.",
            'should_transition': True,
            'target_node': "N_Finalize_And_EndCall_V1_Adaptive",
            'retry_goal': False,
            'identified_objection': "reply_sent",
            'selected_strategy': "confirm_reply_sent"
        }

        MockNodes.get.return_value = {
            'id': 'N_ConfirmAndRequestReply_V4_PatientListener',
            'goal': 'confirm and request reply',
            'transitions': {'default': 'N_Finalize_And_EndCall_V1_Adaptive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_ConfirmAndRequestReply_V4_PatientListener",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        sent_responses = [
            "Okay, I just sent it.",
            "Done.",
            "Done",
            "Sent",
            "Replied",
            "I did it",
            "Okay"
        ]
        
        for response in sent_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_ConfirmAndRequestReply_V4_PatientListener', 'goal': 'confirm and request reply', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Finalize_And_EndCall_V1_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_ConfirmAndRequestReply_V4_PatientListener transition tests passed!\n")


@pytest.mark.asyncio
async def test_finalize_and_end_call_transitions():
    """Test the N_Finalize_And_EndCall_V1_Adaptive node transitions."""
    print("Testing N_Finalize_And_EndCall_V1_Adaptive transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Great talking to you! Goodbye.",
            'should_transition': True,
            'target_node': "N_EndCall_Final_V2_Decisive",
            'retry_goal': False,
            'identified_objection': "end_call",
            'selected_strategy': "finalize_call"
        }

        MockNodes.get.return_value = {
            'id': 'N_Finalize_And_EndCall_V1_Adaptive',
            'goal': 'finalize and end call',
            'transitions': {'default': 'N_EndCall_Final_V2_Decisive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Finalize_And_EndCall_V1_Adaptive",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        any_responses = [
            "Okay, thanks.",
            "Thanks",
            "Bye",
            "Goodbye"
        ]
        
        for response in any_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Finalize_And_EndCall_V1_Adaptive', 'goal': 'finalize and end call', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_EndCall_Final_V2_Decisive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Finalize_And_EndCall_V1_Adaptive transition tests passed!\n")


@pytest.mark.asyncio
async def test_end_call_final_transitions():
    """Test the N_EndCall_Final_V2_Decisive node transitions."""
    print("Testing N_EndCall_Final_V2_Decisive transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "You too! Goodbye.",
            'should_transition': True,
            'target_node': "END_CALL",
            'retry_goal': False,
            'identified_objection': "end_call",
            'selected_strategy': "end_call"
        }

        MockNodes.get.return_value = {
            'id': 'N_EndCall_Final_V2_Decisive',
            'goal': 'end call final',
            'transitions': {'default': 'END_CALL'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_EndCall_Final_V2_Decisive",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        any_responses = [
            "Thanks, you too.",
            "Okay, bye.",
            "Goodbye",
            "See you later",
            "Take care"
        ]
        
        for response in any_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_EndCall_Final_V2_Decisive', 'goal': 'end call final', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("END_CALL", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_EndCall_Final_V2_Decisive transition tests passed!\n")
