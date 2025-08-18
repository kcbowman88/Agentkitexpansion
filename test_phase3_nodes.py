#!/usr/bin/env python3
"""
Test script for verifying the content-based transition logic implementation for Phase 3 untested nodes.
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
async def test_employed_side_hustle_amount_transitions():
    """Test the N201C_Employed_AskSideHustleAmount_V3_FullyTuned node transitions."""
    print("Testing N201C_Employed_AskSideHustleAmount_V3_FullyTuned transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Okay, I understand. Let's move on.",
            'should_transition': True,
            'target_node': "N201D_Employed_AskVehicleQ_V5_Adaptive",
            'retry_goal': False,
            'identified_objection': None,
            'selected_strategy': None
        }

        MockNodes.get.return_value = {
            'id': 'N201C_Employed_AskSideHustleAmount_V3_FullyTuned',
            'goal': 'ask side hustle amount',
            'transitions': {'default': 'N201D_Employed_AskVehicleQ_V5_Adaptive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N201C_Employed_AskSideHustleAmount_V3_FullyTuned",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        any_responses = [
            "A few hundred bucks a month.",
            "It's not much.",
            "About $500 monthly",
            "It varies",
            "Maybe a thousand"
        ]
        
        for response in any_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N201C_Employed_AskSideHustleAmount_V3_FullyTuned', 'goal': 'ask side hustle amount', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N201D_Employed_AskVehicleQ_V5_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N201C_Employed_AskSideHustleAmount_V3_FullyTuned transition tests passed!\n")


@pytest.mark.asyncio
async def test_unemployed_income_transitions():
    """Test the N201E_Unemployed_EmpathyAskPastYearlyIncome_V5_Adaptive node transitions."""
    print("Testing N201E_Unemployed_EmpathyAskPastYearlyIncome_V5_Adaptive transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Okay, I understand. Let's move on.",
            'should_transition': True,
            'target_node': "N201F_Unemployed_AskSideHustle_V4_FullyTuned",
            'retry_goal': False,
            'identified_objection': None,
            'selected_strategy': None
        }

        MockNodes.get.return_value = {
            'id': 'N201E_Unemployed_EmpathyAskPastYearlyIncome_V5_Adaptive',
            'goal': 'ask past yearly income',
            'transitions': {'default': 'N201F_Unemployed_AskSideHustle_V4_FullyTuned'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N201E_Unemployed_EmpathyAskPastYearlyIncome_V5_Adaptive",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        any_responses = [
            "I was making around 70,000.",
            "I don't want to talk about it.",
            "It was about 60k",
            "I'd rather not say",
            "That's personal"
        ]
        
        for response in any_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N201E_Unemployed_EmpathyAskPastYearlyIncome_V5_Adaptive', 'goal': 'ask past yearly income', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N201F_Unemployed_AskSideHustle_V4_FullyTuned", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N201E_Unemployed_EmpathyAskPastYearlyIncome_V5_Adaptive transition tests passed!\n")


@pytest.mark.asyncio
async def test_unemployed_side_hustle_amount_transitions():
    """Test the N201G_Unemployed_AskSideHustleAmount node transitions."""
    print("Testing N201G_Unemployed_AskSideHustleAmount transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Okay, I understand. Let's move on.",
            'should_transition': True,
            'target_node': "N201H_Unemployed_AskVehicleQ_V4_FullyTuned",
            'retry_goal': False,
            'identified_objection': None,
            'selected_strategy': None
        }

        MockNodes.get.return_value = {
            'id': 'N201G_Unemployed_AskSideHustleAmount',
            'goal': 'ask side hustle amount',
            'transitions': {'default': 'N201H_Unemployed_AskVehicleQ_V4_FullyTuned'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N201G_Unemployed_AskSideHustleAmount",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        any_responses = [
            "Maybe five hundred a month.",
            "It varies.",
            "About $300",
            "Sometimes more, sometimes less",
            "It's not consistent"
        ]
        
        for response in any_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N201G_Unemployed_AskSideHustleAmount', 'goal': 'ask side hustle amount', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N201H_Unemployed_AskVehicleQ_V4_FullyTuned", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N201G_Unemployed_AskSideHustleAmount transition tests passed!\n")


@pytest.mark.asyncio
async def test_business_revenue_transitions():
    """Test the N202B_AskHighestRevenueMonth_V4_FullyTuned node transitions."""
    print("Testing N202B_AskHighestRevenueMonth_V4_FullyTuned transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Okay, I understand. Let's move on.",
            'should_transition': True,
            'target_node': "N202C_AskVehicleQuestion_BusinessOwner_V4_Adaptive",
            'retry_goal': False,
            'identified_objection': None,
            'selected_strategy': None
        }

        MockNodes.get.return_value = {
            'id': 'N202B_AskHighestRevenueMonth_V4_FullyTuned',
            'goal': 'ask highest revenue month',
            'transitions': {'default': 'N202C_AskVehicleQuestion_BusinessOwner_V4_Adaptive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N202B_AskHighestRevenueMonth_V4_FullyTuned",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        any_responses = [
            "We hit 50k last December.",
            "I'm not sure.",
            "It was around 40k",
            "We peaked at 60k",
            "I don't remember exactly"
        ]
        
        for response in any_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N202B_AskHighestRevenueMonth_V4_FullyTuned', 'goal': 'ask highest revenue month', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N202C_AskVehicleQuestion_BusinessOwner_V4_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N202B_AskHighestRevenueMonth_V4_FullyTuned transition tests passed!\n")


@pytest.mark.asyncio
async def test_partner_availability_transitions():
    """Test the N018_ConfirmPartnerAvailability node transitions."""
    print("Testing N018_ConfirmPartnerAvailability transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        
        # Mock for partner available responses
        mock_orchestrator_instance.generate_response.side_effect = [
            {
                'response': "Great! I'll make a note of that. Let's move on.",
                'should_transition': True,
                'target_node': "N_AskCapital_15k_V1_Adaptive",
                'retry_goal': False,
                'identified_objection': "available",
                'selected_strategy': "confirm_partner_availability"
            } for _ in range(7) # For each available response
        ] + [
            # Mock for partner not available responses
            {
                'response': "Okay, I understand. We can proceed without them, or I can schedule a call when they're available.",
                'should_transition': True,
                'target_node': "N_AskCapital_15k_V1_Adaptive", # Example transition
                'retry_goal': False,
                'identified_objection': "not_available",
                'selected_strategy': "offer_reschedule"
            } for _ in range(5) # For each not available response
        ] + [
            # Mock for partner schedule uncertain responses
            {
                'response': "Okay, I understand. Please check with them and we can schedule a call when you both are available.",
                'should_transition': True,
                'target_node': "N_AskCapital_15k_V1_Adaptive", # Example transition
                'retry_goal': False,
                'identified_objection': "unsure",
                'selected_strategy': "suggest_follow_up"
            } for _ in range(5) # For each uncertain response
        ]

        MockNodes.get.return_value = {
            'id': 'N018_ConfirmPartnerAvailability',
            'goal': 'confirm partner availability',
            'transitions': {
                'available': 'N_AskCapital_15k_V1_Adaptive',
                'not_available': 'N_AskCapital_15k_V1_Adaptive',
                'unsure': 'N_AskCapital_15k_V1_Adaptive',
                'default': 'N_EndCall_Final_V2_Decisive'
            },
            'transition_conditions': {
                'available': ['yes', 'that works for us', 'she\'ll be there', 'he\'s free', 'works for us', 'i\'m the decision maker', 'yes, we can both be there'],
                'not_available': ['no', 'that won\'t work for my partner', 'she can\'t', 'he\'s busy', 'no, she can\'t make that time'],
                'unsure': ['i don\'t know', 'i\'ll have to check', 'i\'m not sure', 'i don\'t know her schedule', 'i\'ll have to check with him']
            }
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N018_ConfirmPartnerAvailability",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test partner available responses
        available_responses = [
            "Yes, we can both be there.",
            "That works for us.",
            "Yes",
            "She'll be there",
            "He's free",
            "Works for us",
            "I'm the decision maker"
        ]
        
        for response in available_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N018_ConfirmPartnerAvailability', 'goal': 'confirm partner availability', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_AskCapital_15k_V1_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (available) handled correctly.")
        
        # Test partner not available responses
        not_available_responses = [
            "No, she can't make that time.",
            "That won't work for my partner.",
            "No",
            "She can't",
            "He's busy"
        ]
        
        for response in not_available_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N018_ConfirmPartnerAvailability', 'goal': 'confirm partner availability', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_AskCapital_15k_V1_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (not available) handled correctly.")
        
        # Test partner schedule uncertain responses
        uncertain_responses = [
            "I don't know her schedule.",
            "I'll have to check with him.",
            "I don't know",
            "I'll have to check",
            "I'm not sure"
        ]
        
        for response in uncertain_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N018_ConfirmPartnerAvailability', 'goal': 'confirm partner availability', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_AskCapital_15k_V1_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (uncertain) handled correctly.")
    
    print("All N018_ConfirmPartnerAvailability transition tests passed!\n")


@pytest.mark.asyncio
async def test_suggest_partner_check_transitions():
    """Test the N017D_SuggestPartnerCheck_ScheduleFollowUpCall node transitions."""
    print("Testing N017D_SuggestPartnerCheck_ScheduleFollowUpCall transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        mock_orchestrator_instance.generate_response.return_value = {
            'response': "Great! I'll send you a calendar invite. Is there anything else?",
            'should_transition': True,
            'target_node': "N_EndCall_Final_V2_Decisive",
            'retry_goal': False,
            'identified_objection': "follow_up_plan_agreed",
            'selected_strategy': "schedule_follow_up"
        }

        MockNodes.get.return_value = {
            'id': 'N017D_SuggestPartnerCheck_ScheduleFollowUpCall',
            'goal': 'suggest partner check',
            'transitions': {'default': 'N_EndCall_Final_V2_Decisive'},
            'transition_conditions': {}
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="N017D_SuggestPartnerCheck_ScheduleFollowUpCall",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        agreed_responses = [
            "Yes, that sounds fair.",
            "Okay, that works.",
            "Yes",
            "Sounds fair",
            "Okay",
            "Sounds good",
            "That works"
        ]
        
        for response in agreed_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'N017D_SuggestPartnerCheck_ScheduleFollowUpCall', 'goal': 'suggest partner check', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_EndCall_Final_V2_Decisive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' handled correctly.")
    
    print("All N017D_SuggestPartnerCheck_ScheduleFollowUpCall transition tests passed!\n")


@pytest.mark.asyncio
async def test_logic_split_node_transitions():
    """Test the Logic_Split_Node_Financial_Qualification node transitions."""
    print("Testing Logic_Split_Node_Financial_Qualification transitions...")
    
    with patch('caller_agent.ResponseOrchestrator') as MockResponseOrchestrator, \
         patch('caller_agent.nodes') as MockNodes:
        mock_orchestrator_instance = MockResponseOrchestrator.return_value
        
        # Mock for high income responses
        mock_orchestrator_instance.generate_response.side_effect = [
            {
                'response': "Great! That sounds like a strong financial position. Let's move on.",
                'should_transition': True,
                'target_node': "N_AskCapital_15k_V1_Adaptive", # Example transition
                'retry_goal': False,
                'identified_objection': "high_income",
                'selected_strategy': "financial_qualification"
            } for _ in range(12) # For each high income response
        ] + [
            # Mock for standard income responses
            {
                'response': "Okay, I understand. Let's move on.",
                'should_transition': True,
                'target_node': "N_AskCapital_5k_Direct_V1_Adaptive", # Example transition
                'retry_goal': False,
                'identified_objection': "standard_income",
                'selected_strategy': "financial_qualification"
            } for _ in range(4) # For each standard income response
        ]

        MockNodes.get.return_value = {
            'id': 'Logic_Split_Node_Financial_Qualification',
            'goal': 'financial qualification',
            'transitions': {
                'high_income': 'N_AskCapital_15k_V1_Adaptive',
                'standard_income': 'N_AskCapital_5k_Direct_V1_Adaptive',
                'default': 'N_EndCall_Final_V2_Decisive'
            },
            'transition_conditions': {
                'high_income': ['100k', '100,000', '100 thousand', 'eight thousand', '8000', 'six figures', '150k', '150,000', '200k', '200,000', 'high earner', 'substantial income'],
                'standard_income': ['50k', 'i make less than that', 'not much', 'just starting out']
            }
        }

        agent = CallFlowAgent()
        agent.session = MagicMock()
        agent.session.userdata = CallFlowState(
            customer_name="Test User",
            current_node_id="Logic_Split_Node_Financial_Qualification",
            conversation_history=[]
        )
        agent._safe_say = AsyncMock(return_value=True)
        agent._transition_to_node = AsyncMock(return_value=None)
        agent._enforce_final_turn_compliance = MagicMock(side_effect=lambda state, text, node_data, will_transition: text)
        agent.conversation_state_manager.record_strategy_use = MagicMock()

        # Test high income responses
        high_income_responses = [
            "100k",
            "100,000",
            "100 thousand",
            "eight thousand",
            "8000",
            "six figures",
            "150k",
            "150,000",
            "200k",
            "200,000",
            "high earner",
            "substantial income"
        ]
        
        for response in high_income_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'Logic_Split_Node_Financial_Qualification', 'goal': 'financial qualification', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_AskCapital_15k_V1_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (high income) handled correctly.")
        
        # Test standard income responses (responses that don't match high income patterns)
        standard_income_responses = [
            "50k",
            "I make less than that",
            "Not much",
            "Just starting out"
        ]
        
        for response in standard_income_responses:
            print(f"User: {response}")
            await agent._handle_user_response(response, agent.session.userdata)
            
            mock_orchestrator_instance.generate_response.assert_called_with(
                response,
                {'id': 'Logic_Split_Node_Financial_Qualification', 'goal': 'financial qualification', 'transitions': MockNodes.get.return_value['transitions'], 'transition_conditions': MockNodes.get.return_value['transition_conditions']}
            )
            agent._safe_say.assert_called_once()
            agent._transition_to_node.assert_called_once_with("N_AskCapital_5k_Direct_V1_Adaptive", suppress_script=True)
            
            mock_orchestrator_instance.generate_response.reset_mock()
            agent._safe_say.reset_mock()
            agent._transition_to_node.reset_mock()
            
            print(f"✓ '{response}' (standard income) handled correctly.")
    
    print("All Logic_Split_Node_Financial_Qualification transition tests passed!\n")
