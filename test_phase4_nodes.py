#!/usr/bin/env python3
"""
Test script for verifying the content-based transition logic implementation for Phase 4 untested nodes.
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
async def test_why_now_transitions():
    """Test the N401_AskWhyNow_Initial_V10_AssertiveFrame node transitions."""
    print("Testing N401_AskWhyNow_Initial_V10_AssertiveFrame transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        
        # Mock for motivation provided responses
        mock_orchestrator_instance.generate_response.side_effect = [
            {
                'response': "I understand you're looking for more freedom. Let's explore that.",
                'should_transition': True,
                'target_node': "N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned",
                'retry_goal': False,
                'identified_objection': "motivation_provided",
                'selected_strategy': "explore_motivation"
            } for _ in range(6) # For each motivation response
        ] + [
            # Mock for callback requested responses
            {
                'response': "I understand you have to go. Can I schedule a brief call for later?",
                'should_transition': True,
                'target_node': "N_Obj_RealBusy_OfferReschedule",
                'retry_goal': False,
                'identified_objection': "callback_requested",
                'selected_strategy': "reschedule"
            } for _ in range(3) # For each callback response
        ]

        MockNodes.get.return_value = {
            'id': 'N401_AskWhyNow_Initial_V10_AssertiveFrame',
            'goal': 'ask why now',
            'transitions': {
                'motivation_provided': 'N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned',
                'callback_requested': 'N_Obj_RealBusy_OfferReschedule',
                'default': 'N_EndCall_Final_V2_Decisive'
            },
            'transition_conditions': {
                'motivation_provided': ['freedom', 'tired of my job', 'need more income', 'for my family', 'i\'m just tired of the 9-to-5 and need more freedom', 'i\'m looking for a real change'],
                'callback_requested': ['have to go', 'busy', 'i have to go now']
            }
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N401_AskWhyNow_Initial_V10_AssertiveFrame",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test motivation provided responses
        motivation_responses = [
            "I'm just tired of the 9-to-5 and need more freedom.",
            "I'm looking for a real change.",
            "Freedom",
            "Tired of my job",
            "Need more income",
            "For my family"
        ]
        
        for response in motivation_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N401_AskWhyNow_Initial_V10_AssertiveFrame', 'goal': 'ask why now', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (motivation) handled correctly.")
        
        # Test callback requested responses
        callback_responses = [
            "I have to go now.",
            "Have to go",
            "Busy"
        ]
        
        for response in callback_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N401_AskWhyNow_Initial_V10_AssertiveFrame', 'goal': 'ask why now', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Obj_RealBusy_OfferReschedule", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (callback) handled correctly.")
    
    print("All N401_AskWhyNow_Initial_V10_AssertiveFrame transition tests passed!\n")


@pytest.mark.asyncio
async def test_compliment_transitions():
    """Test the N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned node transitions."""
    print("Testing N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        
        # Mock for any response (default)
        mock_orchestrator_instance.generate_response.side_effect = [
            {
                'response': "I understand you're curious. We help local businesses rank higher on Google. Does that make sense?",
                'should_transition': True,
                'target_node': "N_IntroduceModel_And_AskQuestions_V3_Adaptive",
                'retry_goal': False,
                'identified_objection': "responded_to_hook",
                'selected_strategy': "explain_model"
            } for _ in range(5) # For each any response
        ] + [
            # Mock for callback requested responses
            {
                'response': "I understand you have to go. Can I schedule a brief call for later?",
                'should_transition': True,
                'target_node': "N_Obj_RealBusy_OfferReschedule",
                'retry_goal': False,
                'identified_objection': "callback_requested",
                'selected_strategy': "reschedule"
            } for _ in range(3) # For each callback response
        ]

        MockNodes.get.return_value = {
            'id': 'N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned',
            'goal': 'compliment and ask why',
            'transitions': {
                'responded_to_hook': 'N_IntroduceModel_And_AskQuestions_V3_Adaptive',
                'callback_requested': 'N_Obj_RealBusy_OfferReschedule',
                'default': 'N_EndCall_Final_V2_Decisive'
            },
            'transition_conditions': {
                'responded_to_hook': ['why', 'no, why', 'okay', 'i\'m not sure', 'what do you mean'],
                'callback_requested': ['have to go', 'busy', 'i\'ve got to run']
            }
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test any response (default)
        any_responses = [
            "Why?",
            "No, why?",
            "Okay...",
            "I'm not sure",
            "What do you mean?"
        ]
        
        for response in any_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned', 'goal': 'compliment and ask why', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_IntroduceModel_And_AskQuestions_V3_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (any response) handled correctly.")
        
        # Test callback requested responses
        callback_responses = [
            "I've got to run.",
            "Have to go",
            "Busy"
        ]
        
        for response in callback_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned', 'goal': 'compliment and ask why', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Obj_RealBusy_OfferReschedule", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (callback) handled correctly.")
    
    print("All N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned transition tests passed!\n")


@pytest.mark.asyncio
async def test_identity_affirmation_transitions():
    """Test the N403_IdentityAffirmation_And_ValueFitQuestion_V8_GoalAligned node transitions."""
    print("Testing N403_IdentityAffirmation_And_ValueFitQuestion_V8_GoalAligned transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        
        # Mock for value confirmed responses
        mock_orchestrator_instance.generate_response.side_effect = [
            {
                'response': "Great! It sounds like this is a good fit. Let's move on.",
                'should_transition': True,
                'target_node': "N500A_ProposeDeeperDive_V5_Adaptive",
                'retry_goal': False,
                'identified_objection': "fits",
                'selected_strategy': "propose_deeper_dive"
            } for _ in range(5) # For each value confirmed response
        ] + [
            # Mock for callback requested responses
            {
                'response': "I understand you have to go. Can I schedule a brief call for later?",
                'should_transition': True,
                'target_node': "N_Obj_RealBusy_OfferReschedule",
                'retry_goal': False,
                'identified_objection': "callback_requested",
                'selected_strategy': "reschedule"
            } for _ in range(3) # For each callback response
        ]

        MockNodes.get.return_value = {
            'id': 'N403_IdentityAffirmation_And_ValueFitQuestion_V8_GoalAligned',
            'goal': 'identity affirmation',
            'transitions': {
                'fits': 'N500A_ProposeDeeperDive_V5_Adaptive',
                'callback_requested': 'N_Obj_RealBusy_OfferReschedule',
                'default': 'N_EndCall_Final_V2_Decisive'
            },
            'transition_conditions': {
                'fits': ['yes', 'it does', 'sounds like it', 'exactly what i\'m looking for', 'yes, this sounds like what i\'m looking for'],
                'callback_requested': ['have to go', 'busy', 'i have to go']
            }
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N403_IdentityAffirmation_And_ValueFitQuestion_V8_GoalAligned",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test value confirmed responses
        value_confirmed_responses = [
            "Yes, this sounds like what I'm looking for.",
            "Yes",
            "It does",
            "Sounds like it",
            "Exactly what I'm looking for"
        ]
        
        for response in value_confirmed_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N403_IdentityAffirmation_And_ValueFitQuestion_V8_GoalAligned', 'goal': 'identity affirmation', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N500A_ProposeDeeperDive_V5_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (value confirmed) handled correctly.")
        
        # Test callback requested responses
        callback_responses = [
            "I have to go.",
            "Have to go",
            "Busy"
        ]
        
        for response in callback_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N403_IdentityAffirmation_And_ValueFitQuestion_V8_GoalAligned', 'goal': 'identity affirmation', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Obj_RealBusy_OfferReschedule", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (callback) handled correctly.")
    
    print("All N403_IdentityAffirmation_And_ValueFitQuestion_V8_GoalAligned transition tests passed!\n")


@pytest.mark.asyncio
async def test_ask_timezone_transitions():
    """Test the N500B_AskTimezone_V2_FullyTuned node transitions."""
    print("Testing N500B_AskTimezone_V2_FullyTuned transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Okay, I've noted your timezone. Let's move on.",
            'should_transition': True,
            'target_node': "N_AskForCallbackRange_V1_Adaptive",
            'retry_goal': False,
            'identified_objection': "timezone_provided",
            'selected_strategy': "confirm_timezone"
        }

        MockNodes.get.return_value = {
            'id': 'N500B_AskTimezone_V2_FullyTuned',
            'goal': 'ask timezone',
            'transitions': {'default': 'N_AskForCallbackRange_V1_Adaptive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N500B_AskTimezone_V2_FullyTuned",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        timezone_responses = [
            "I'm on Eastern time.",
            "Pacific.",
            "I'm in Denver.",
            "eastern",
            "mountain",
            "central",
            "PST",
            "EST"
        ]
        
        for response in timezone_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N500B_AskTimezone_V2_FullyTuned', 'goal': 'ask timezone', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_AskForCallbackRange_V1_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N500B_AskTimezone_V2_FullyTuned transition tests passed!\n")


@pytest.mark.asyncio
async def test_ask_callback_range_transitions():
    """Test the N_AskForCallbackRange_V1_Adaptive node transitions."""
    print("Testing N_AskForCallbackRange_V1_Adaptive transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Okay, I've noted your preferred callback time. Let's move on.",
            'should_transition': True,
            'target_node': "N_Scheduling_AskTime_V2_SmartAmbiguity",
            'retry_goal': False,
            'identified_objection': "range_provided",
            'selected_strategy': "confirm_callback_range"
        }

        MockNodes.get.return_value = {
            'id': 'N_AskForCallbackRange_V1_Adaptive',
            'goal': 'ask callback range',
            'transitions': {'default': 'N_Scheduling_AskTime_V2_SmartAmbiguity'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_AskForCallbackRange_V1_Adaptive",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        range_responses = [
            "Usually afternoons are good.",
            "Anytime after 3 PM.",
            "Afternoon",
            "Morning",
            "Between 2 and 4",
            "After 5"
        ]
        
        for response in range_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_AskForCallbackRange_V1_Adaptive', 'goal': 'ask callback range', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Scheduling_AskTime_V2_SmartAmbiguity", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_AskForCallbackRange_V1_Adaptive transition tests passed!\n")


@pytest.mark.asyncio
async def test_scheduling_ask_time_transitions():
    """Test the N_Scheduling_AskTime_V2_SmartAmbiguity node transitions."""
    print("Testing N_Scheduling_AskTime_V2_SmartAmbiguity transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Okay, I've noted the time. Let's move on.",
            'should_transition': True,
            'target_node': "N_ConfirmVideoCallEnvironment_V1_Adaptive",
            'retry_goal': False,
            'identified_objection': "time_provided",
            'selected_strategy': "confirm_time"
        }

        MockNodes.get.return_value = {
            'id': 'N_Scheduling_AskTime_V2_SmartAmbiguity',
            'goal': 'scheduling ask time',
            'transitions': {'default': 'N_ConfirmVideoCallEnvironment_V1_Adaptive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Scheduling_AskTime_V2_SmartAmbiguity",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        time_responses = [
            "How about 3 PM?",
            "Let's do 10 AM tomorrow.",
            "3 PM",
            "10 AM tomorrow",
            "Tomorrow at 2"
        ]
        
        for response in time_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Scheduling_AskTime_V2_SmartAmbiguity', 'goal': 'scheduling ask time', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_ConfirmVideoCallEnvironment_V1_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_Scheduling_AskTime_V2_SmartAmbiguity transition tests passed!\n")


@pytest.mark.asyncio
async def test_confirm_video_call_environment_transitions():
    """Test the N_ConfirmVideoCallEnvironment_V1_Adaptive node transitions."""
    print("Testing N_ConfirmVideoCallEnvironment_V1_Adaptive transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Great! I'll send you the meeting link. Let's move on.",
            'should_transition': True,
            'target_node': "N_Video_Assign_GentleIntro_V3_FullyTuned",
            'retry_goal': False,
            'identified_objection': "confirmed",
            'selected_strategy': "confirm_environment"
        }

        MockNodes.get.return_value = {
            'id': 'N_ConfirmVideoCallEnvironment_V1_Adaptive',
            'goal': 'confirm video call environment',
            'transitions': {'default': 'N_Video_Assign_GentleIntro_V3_FullyTuned'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_ConfirmVideoCallEnvironment_V1_Adaptive",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        confirmed_responses = [
            "Yes, I can be at my computer then.",
            "That works for me.",
            "Yes",
            "That works",
            "I can do that"
        ]
        
        for response in confirmed_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_ConfirmVideoCallEnvironment_V1_Adaptive', 'goal': 'confirm video call environment', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Video_Assign_GentleIntro_V3_FullyTuned", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N_ConfirmVideoCallEnvironment_V1_Adaptive transition tests passed!\n")


@pytest.mark.asyncio
async def test_scheduling_reschedule_transitions():
    """Test the N_Scheduling_RescheduleAndHandle_V5_FullyTuned node transitions."""
    print("Testing N_Scheduling_RescheduleAndHandle_V5_FullyTuned transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        
        # Mock for time booked successfully responses
        mock_orchestrator_instance.generate_response.side_effect = [
            {
                'response': "Great! I've updated your appointment. Is there anything else?",
                'should_transition': True,
                'target_node': "N_EndCall_Final_V2_Decisive",
                'retry_goal': False,
                'identified_objection': "new_time_found",
                'selected_strategy': "confirm_reschedule"
            } for _ in range(8) # For each success response
        ] + [
            # Mock for time unavailable responses
            {
                'response': "I understand that time doesn't work. Can you suggest another time?",
                'should_transition': True,
                'target_node': "N_Scheduling_AskTime_V2_SmartAmbiguity",
                'retry_goal': False,
                'identified_objection': "time_unavailable",
                'selected_strategy': "ask_for_new_time"
            } for _ in range(7) # For each unavailable response
        ] + [
            # Mock for user picks new time responses
            {
                'response': "Okay, I've noted that time. Let me check if it's available.",
                'should_transition': True,
                'target_node': "N_Scheduling_ConfirmRescheduleTime",
                'retry_goal': False,
                'identified_objection': "user_picks_new_time",
                'selected_strategy': "confirm_new_time"
            } for _ in range(7) # For each new time response
        ] + [
            # Mock for hostile or end call responses
            {
                'response': "I understand you're not interested. Is there anything else I can help you with?",
                'should_transition': True,
                'target_node': "N_EndCall_Final_V2_Decisive",
                'retry_goal': False,
                'identified_objection': "hostile_or_end_call",
                'selected_strategy': "end_call"
            } for _ in range(8) # For each hostile response
        ]

        MockNodes.get.return_value = {
            'id': 'N_Scheduling_RescheduleAndHandle_V5_FullyTuned',
            'goal': 'scheduling reschedule',
            'transitions': {
                'new_time_found': 'N_EndCall_Final_V2_Decisive',
                'time_unavailable': 'N_Scheduling_AskTime_V2_SmartAmbiguity',
                'user_picks_new_time': 'N_Scheduling_ConfirmRescheduleTime',
                'hostile_or_end_call': 'N_EndCall_Final_V2_Decisive',
                'default': 'N_EndCall_Final_V2_Decisive'
            },
            'transition_conditions': {
                'new_time_found': ['great', 'perfect', 'sounds good', 'works for me', 'that\'s fine', 'i\'m available', 'i can make it', 'that works'],
                'time_unavailable': ['not available', 'unavailable', 'conflict', 'busy', 'taken', 'booked', 'not free'],
                'user_picks_new_time': ['how about', 'what about', 'is X available', 'can we do', 'what time', 'when can', 'alternative'],
                'hostile_or_end_call': ['no', 'nevermind', 'forget it', 'not interested', 'don\'t call', 'stop calling', 'go away', 'leave me alone']
            }
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N_Scheduling_RescheduleAndHandle_V5_FullyTuned",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test time booked successfully responses
        success_responses = [
            "Great.",
            "Perfect.",
            "Sounds good.",
            "Works for me.",
            "That's fine.",
            "I'm available.",
            "I can make it.",
            "That works."
        ]
        
        for response in success_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Scheduling_RescheduleAndHandle_V5_FullyTuned', 'goal': 'scheduling reschedule', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_EndCall_Final_V2_Decisive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (success) handled correctly.")
        
        # Test time unavailable responses
        unavailable_responses = [
            "Not available.",
            "Unavailable.",
            "Conflict.",
            "Busy.",
            "Taken.",
            "Booked.",
            "Not free."
        ]
        
        for response in unavailable_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Scheduling_RescheduleAndHandle_V5_FullyTuned', 'goal': 'scheduling reschedule', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Scheduling_AskTime_V2_SmartAmbiguity", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (unavailable) handled correctly.")
        
        # Test user picks new time responses
        new_time_responses = [
            "How about",
            "What about",
            "Is X available",
            "Can we do",
            "What time",
            "When can",
            "Alternative"
        ]
        
        for response in new_time_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Scheduling_RescheduleAndHandle_V5_FullyTuned', 'goal': 'scheduling reschedule', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_Scheduling_ConfirmRescheduleTime", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (user picks new time) handled correctly.")
        
        # Test hostile or end call responses
        hostile_responses = [
            "No",
            "Nevermind",
            "Forget it",
            "Not interested",
            "Don't call",
            "Stop calling",
            "Go away",
            "Leave me alone"
        ]
        
        for response in hostile_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N_Scheduling_RescheduleAndHandle_V5_FullyTuned', 'goal': 'scheduling reschedule', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_EndCall_Final_V2_Decisive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (hostile) handled correctly.")
    
    print("All N_Scheduling_RescheduleAndHandle_V5_FullyTuned transition tests passed!\n")
