#!/usr/bin/env python3
"""
Test script for verifying the content-based transition logic implementation for Phase 2 untested nodes.
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
async def test_early_dismiss_share_background_ask_why_transitions():
    """Test the N_Obj_EarlyDismiss_ShareBackgroundAskWhy (V1) node transitions."""
    print("Testing N_Obj_EarlyDismiss_ShareBackgroundAskWhy (V1) transitions...")
    
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
            'id': 'N_Obj_EarlyDismiss_ShareBackgroundAskWhy',
            'goal': 'share background',
            'transitions': {'default': 'N_IntroduceModel_And_AskQuestions_V3_Adaptive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Obj_EarlyDismiss_ShareBackgroundAskWhy",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        any_responses = [
            "Why?",
            "No."
        ]
        
        for response in any_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_EarlyDismiss_ShareBackgroundAskWhy', 'goal': 'share background', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_IntroduceModel_And_AskQuestions_V3_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Obj_EarlyDismiss_ShareBackgroundAskWhy (V1) transition tests passed!\n")


@pytest.mark.asyncio
async def test_early_dismiss_direct_value_challenge_transitions():
    """Test the N_Obj_EarlyDismiss_DirectValueChallenge (V1) node transitions."""
    print("Testing N_Obj_EarlyDismiss_DirectValueChallenge (V1) transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "I understand your skepticism. Many people are curious about how this works. Would you like me to explain further?",
            'should_transition': True,
            'target_node': "N_KB_Q&A_With_StrategicNarrative_V3_Adaptive",
            'retry_goal': False,
            'identified_objection': "direct_challenge_accepted",
            'selected_strategy': "deframe"
        }

        MockNodes.get.return_value = {
            'id': 'N_Obj_EarlyDismiss_DirectValueChallenge',
            'goal': 'direct value challenge',
            'transitions': {'default': 'N_KB_Q&A_With_StrategicNarrative_V3_Adaptive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Obj_EarlyDismiss_DirectValueChallenge",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        challenge_accepted_responses = [
            "Yes.",
            "Depends.",
            "What is it"
        ]
        
        for response in challenge_accepted_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_EarlyDismiss_DirectValueChallenge', 'goal': 'direct value challenge', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_KB_Q&A_With_StrategicNarrative_V3_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Obj_EarlyDismiss_DirectValueChallenge (V1) transition tests passed!\n")


@pytest.mark.asyncio
async def test_early_dismiss_explain_reason_transitions():
    """Test the N_Obj_EarlyDismiss_ExplainReasonAndExplore (V1) node transitions."""
    print("Testing N_Obj_EarlyDismiss_ExplainReasonAndExplore (V1) transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        
        # Mock for success responses
        mock_orchestrator_instance.generate_response.side_effect = [
            {
                'response': "I understand that sounds interesting. We help local businesses rank higher on Google. Would you like to know more?",
                'should_transition': True,
                'target_node': "N_IntroduceModel_And_AskQuestions_V3_Adaptive",
                'retry_goal': False,
                'identified_objection': "still_interested",
                'selected_strategy': "explain_reason"
            } for _ in range(4) # For each success response
        ] + [
            # Mock for resistant responses
            {
                'response': "I understand you're not interested. Is there anything else I can help you with?",
                'should_transition': True,
                'target_node': "N_EndCall_Final_V2_Decisive",
                'retry_goal': False,
                'identified_objection': "resistant",
                'selected_strategy': "end_call"
            } for _ in range(3) # For each resistant response
        ]

        MockNodes.get.return_value = {
            'id': 'N_Obj_EarlyDismiss_ExplainReasonAndExplore',
            'goal': 'explain reason',
            'transitions': {
                'still_interested': 'N_IntroduceModel_And_AskQuestions_V3_Adaptive',
                'default': 'N_EndCall_Final_V2_Decisive'
            },
            'transition_conditions': {
                'still_interested': ['sounds interesting', 'yes', 'okay', 'sounds interesting'],
                'resistant': ['not interested', 'no', 'not really']
            }
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Obj_EarlyDismiss_ExplainReasonAndExplore",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test early dismiss PSPF1 success responses
        success_responses = [
            "Okay, that sounds interesting.",
            "Yes",
            "Okay",
            "Sounds interesting"
        ]
        
        for response in success_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_EarlyDismiss_ExplainReasonAndExplore', 'goal': 'explain reason', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_IntroduceModel_And_AskQuestions_V3_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (success) handled correctly.")
        
        # Test early dismiss PSPF1 still resistant responses
        resistant_responses = [
            "I'm still not interested.",
            "No",
            "Not really"
        ]
        
        for response in resistant_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_EarlyDismiss_ExplainReasonAndExplore', 'goal': 'explain reason', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_EndCall_Final_V2_Decisive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (resistant) handled correctly.")
    
    print("All N_Obj_EarlyDismiss_ExplainReasonAndExplore (V1) transition tests passed!\n")


@pytest.mark.asyncio
async def test_early_dismiss_connect_to_current_call_transitions():
    """Test the N_Obj_EarlyDismiss_ConnectToCurrentCall (V1) node transitions."""
    print("Testing N_Obj_EarlyDismiss_ConnectToCurrentCall (V1) transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        
        # Mock for exploration agreed responses
        mock_orchestrator_instance.generate_response.side_effect = [
            {
                'response': "I understand you're willing to explore. We help local businesses rank higher on Google. Would you like to know more?",
                'should_transition': True,
                'target_node': "N_IntroduceModel_And_AskQuestions_V3_Adaptive",
                'retry_goal': False,
                'identified_objection': "agrees_to_explore",
                'selected_strategy': "connect_to_current_call"
            } for _ in range(3) # For each exploration response
        ] + [
            # Mock for insists on leaving responses
            {
                'response': "I understand you have to go. Is there anything else I can help you with?",
                'should_transition': True,
                'target_node': "N_EndCall_Final_V2_Decisive",
                'retry_goal': False,
                'identified_objection': "insists_on_leaving",
                'selected_strategy': "end_call"
            } for _ in range(3) # For each leaving response
        ]

        MockNodes.get.return_value = {
            'id': 'N_Obj_EarlyDismiss_ConnectToCurrentCall',
            'goal': 'connect to current call',
            'transitions': {
                'agrees_to_explore': 'N_IntroduceModel_And_AskQuestions_V3_Adaptive',
                'default': 'N_EndCall_Final_V2_Decisive'
            },
            'transition_conditions': {
                'agrees_to_explore': ['let\'s talk', 'yes', 'okay'],
                'insists_on_leaving': ['have to go', 'busy', 'i really have to go']
            }
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Obj_EarlyDismiss_ConnectToCurrentCall",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test exploration agreed responses
        exploration_responses = [
            "Okay, let's talk.",
            "Yes",
            "Okay"
        ]
        
        for response in exploration_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_EarlyDismiss_ConnectToCurrentCall', 'goal': 'connect to current call', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_IntroduceModel_And_AskQuestions_V3_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (exploration) handled correctly.")
        
        # Test insists on leaving responses
        leaving_responses = [
            "I really have to go.",
            "Have to go",
            "Busy"
        ]
        
        for response in leaving_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_EarlyDismiss_ConnectToCurrentCall', 'goal': 'connect to current call', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_EndCall_Final_V2_Decisive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (leaving) handled correctly.")
    
    print("All N_Obj_EarlyDismiss_ConnectToCurrentCall (V1) transition tests passed!\n")


@pytest.mark.asyncio
async def test_real_busy_check_transitions():
    """Test the N_Obj_RealBusy_BluntCheck_V3_Adaptive node transitions."""
    print("Testing N_Obj_RealBusy_BluntCheck_V3_Adaptive transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        
        # Mock for confirmed meeting responses
        mock_orchestrator_instance.generate_response.side_effect = [
            {
                'response': "I understand you have a meeting coming up. How much time do you have?",
                'should_transition': True,
                'target_node': "N_Obj_RealBusy_AskMeetingTime",
                'retry_goal': False,
                'identified_objection': "meeting_coming_up",
                'selected_strategy': "check_time"
            } for _ in range(4) # For each meeting response
        ] + [
            # Mock for value objection responses
            {
                'response': "I understand you're not sure why you're listening. We help local businesses rank higher on Google. Would you like to know more?",
                'should_transition': True,
                'target_node': "N_IntroduceModel_And_AskQuestions_V3_Adaptive",
                'retry_goal': False,
                'identified_objection': "not_sure_why_listening",
                'selected_strategy': "explain_value"
            } for _ in range(4) # For each value objection response
        ]

        MockNodes.get.return_value = {
            'id': 'N_Obj_RealBusy_BluntCheck_V3_Adaptive',
            'goal': 'real busy check',
            'transitions': {
                'meeting_coming_up': 'N_Obj_RealBusy_AskMeetingTime',
                'not_sure_why_listening': 'N_IntroduceModel_And_AskQuestions_V3_Adaptive',
                'default': 'N_EndCall_Final_V2_Decisive'
            },
            'transition_conditions': {
                'meeting_coming_up': ['meeting', 'call soon', 'i really do', 'yes, i have a meeting'],
                'not_sure_why_listening': ['not sure', 'don\'t see the value', 'i\'m skeptical', 'i\'m just not sure this is for me']
            }
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Obj_RealBusy_BluntCheck_V3_Adaptive",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test confirmed meeting responses
        meeting_responses = [
            "Yes, I have a meeting in 10 minutes.",
            "Meeting",
            "I really do",
            "I have a call soon"
        ]
        
        for response in meeting_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_RealBusy_BluntCheck_V3_Adaptive', 'goal': 'real busy check', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Obj_RealBusy_AskMeetingTime", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (meeting) handled correctly.")
        
        # Test value objection responses
        value_objection_responses = [
            "I'm just not sure this is for me.",
            "Not sure",
            "Don't see the value",
            "I'm skeptical"
        ]
        
        for response in value_objection_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_RealBusy_BluntCheck_V3_Adaptive', 'goal': 'real busy check', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_IntroduceModel_And_AskQuestions_V3_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (value objection) handled correctly.")
    
    print("All N_Obj_RealBusy_BluntCheck_V3_Adaptive transition tests passed!\n")


@pytest.mark.asyncio
async def test_real_busy_ask_meeting_time_transitions():
    """Test the N_Obj_RealBusy_AskMeetingTime (V1) node transitions."""
    print("Testing N_Obj_RealBusy_AskMeetingTime (V1) transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        
        # Mock for meeting time given responses
        mock_orchestrator_instance.generate_response.side_effect = [
            {
                'response': "I understand you have a meeting in 5 minutes. Would you like to reschedule?",
                'should_transition': True,
                'target_node': "N_Obj_RealBusy_OfferReschedule",
                'retry_goal': False,
                'identified_objection': "time_given",
                'selected_strategy': "reschedule"
            } for _ in range(3) # For each time given response
        ] + [
            # Mock for meeting time vague responses
            {
                'response': "I understand you're busy soon. How much time do you have?",
                'should_transition': True,
                'target_node': "N_Obj_RealBusy_StateRemainingTimeAndWrapUp",
                'retry_goal': False,
                'identified_objection': "vague",
                'selected_strategy': "wrap_up"
            } for _ in range(3) # For each vague response
        ]

        MockNodes.get.return_value = {
            'id': 'N_Obj_RealBusy_AskMeetingTime',
            'goal': 'ask meeting time',
            'transitions': {
                'time_given': 'N_Obj_RealBusy_OfferReschedule',
                'vague': 'N_Obj_RealBusy_StateRemainingTimeAndWrapUp',
                'default': 'N_EndCall_Final_V2_Decisive'
            },
            'transition_conditions': {
                'time_given': ['in 5 minutes', 'in 10 minutes', 'at 3', 'my meeting is in 5 minutes'],
                'vague': ['soon', 'in a bit', 'it\'s coming up soon']
            }
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Obj_RealBusy_AskMeetingTime",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test meeting time given responses
        time_given_responses = [
            "My meeting is in 5 minutes.",
            "In 10 minutes",
            "At 3"
        ]
        
        for response in time_given_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_RealBusy_AskMeetingTime', 'goal': 'ask meeting time', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Obj_RealBusy_OfferReschedule", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (time given) handled correctly.")
        
        # Test meeting time vague responses
        vague_responses = [
            "It's coming up soon.",
            "Soon",
            "In a bit"
        ]
        
        for response in vague_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_RealBusy_AskMeetingTime', 'goal': 'ask meeting time', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Obj_RealBusy_StateRemainingTimeAndWrapUp", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (vague) handled correctly.")
    
    print("All N_Obj_RealBusy_AskMeetingTime (V1) transition tests passed!\n")


@pytest.mark.asyncio
async def test_real_busy_confirm_reschedule_time_transitions():
    """Test the N_Obj_RealBusy_ConfirmRescheduleTime node transitions."""
    print("Testing N_Obj_RealBusy_ConfirmRescheduleTime transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Great! I've scheduled that for you. I'll send a confirmation. Is there anything else?",
            'should_transition': True,
            'target_node': "N_EndCall_Final_V2_Decisive",
            'retry_goal': False,
            'identified_objection': "confirmed",
            'selected_strategy': "confirm_reschedule"
        }

        MockNodes.get.return_value = {
            'id': 'N_Obj_RealBusy_ConfirmRescheduleTime',
            'goal': 'confirm reschedule time',
            'transitions': {'default': 'N_EndCall_Final_V2_Decisive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Obj_RealBusy_ConfirmRescheduleTime",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        confirmed_responses = [
            "Yes, I'll be 100% available then.",
            "Yes",
            "I will be"
        ]
        
        for response in confirmed_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_RealBusy_ConfirmRescheduleTime', 'goal': 'confirm reschedule time', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_EndCall_Final_V2_Decisive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Obj_RealBusy_ConfirmRescheduleTime transition tests passed!\n")


@pytest.mark.asyncio
async def test_real_busy_offer_reschedule_transitions():
    """Test the N_Obj_RealBusy_OfferReschedule node transitions."""
    print("Testing N_Obj_RealBusy_OfferReschedule transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "I understand. What time works best for you?",
            'should_transition': True,
            'target_node': "N_Obj_RealBusy_ConfirmRescheduleTime",
            'retry_goal': False,
            'identified_objection': "reschedule_time_offered",
            'selected_strategy': "offer_reschedule"
        }

        MockNodes.get.return_value = {
            'id': 'N_Obj_RealBusy_OfferReschedule',
            'goal': 'offer reschedule',
            'transitions': {'default': 'N_Obj_RealBusy_ConfirmRescheduleTime'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Obj_RealBusy_OfferReschedule",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        offered_responses = [
            "How about tomorrow afternoon?",
            "Tomorrow",
            "Next week"
        ]
        
        for response in offered_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_RealBusy_OfferReschedule', 'goal': 'offer reschedule', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Obj_RealBusy_ConfirmRescheduleTime", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Obj_RealBusy_OfferReschedule transition tests passed!\n")


@pytest.mark.asyncio
async def test_real_busy_state_callback_transitions():
    """Test the N_Obj_RealBusy_StateCallbackAndTeaseGuarantees node transitions."""
    print("Testing N_Obj_RealBusy_StateCallbackAndTeaseGuarantees transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Great! I've noted that. Is there anything else I can help you with?",
            'should_transition': True,
            'target_node': "N_EndCall_Final_V2_Decisive",
            'retry_goal': False,
            'identified_objection': "worth_exploring",
            'selected_strategy': "end_call"
        }

        MockNodes.get.return_value = {
            'id': 'N_Obj_RealBusy_StateCallbackAndTeaseGuarantees',
            'goal': 'state callback',
            'transitions': {'default': 'N_EndCall_Final_V2_Decisive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Obj_RealBusy_StateCallbackAndTeaseGuarantees",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        any_responses = [
            "Okay, sounds good.",
            "Sounds good"
        ]
        
        for response in any_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_RealBusy_StateCallbackAndTeaseGuarantees', 'goal': 'state callback', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_EndCall_Final_V2_Decisive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Obj_RealBusy_StateCallbackAndTeaseGuarantees transition tests passed!\n")


@pytest.mark.asyncio
async def test_real_busy_state_remaining_time_transitions():
    """Test the N_Obj_RealBusy_StateRemainingTimeAndWrapUp node transitions."""
    print("Testing N_Obj_RealBusy_StateRemainingTimeAndWrapUp transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "I understand. I'll let you go then. Have a great day!",
            'should_transition': True,
            'target_node': "N_EndCall_Final_V2_Decisive",
            'retry_goal': False,
            'identified_objection': "wrap_up_delivered",
            'selected_strategy': "end_call"
        }

        MockNodes.get.return_value = {
            'id': 'N_Obj_RealBusy_StateRemainingTimeAndWrapUp',
            'goal': 'state remaining time',
            'transitions': {'default': 'N_EndCall_Final_V2_Decisive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Obj_RealBusy_StateRemainingTimeAndWrapUp",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        any_responses = [
            "Okay, thanks.",
            "Thanks"
        ]
        
        for response in any_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Obj_RealBusy_StateRemainingTimeAndWrapUp', 'goal': 'state remaining time', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_EndCall_Final_V2_Decisive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Obj_RealBusy_StateRemainingTimeAndWrapUp transition tests passed!\n")
