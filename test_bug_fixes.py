import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from caller_agent import CallFlowAgent, CallFlowState

# This is a new test file to specifically verify the bug fixes I've implemented.

@pytest.mark.asyncio
@patch('caller_agent.KBProcessor')
async def test_deframe_initial_objection_fallback(MockKBProcessor):
    """
    Tests that if the user does not express curiosity in the N003B node,
    the agent correctly falls back to the escalation node.
    """
    # 1. Setup
    initial_state = CallFlowState(current_node_id="N003B_DeframeInitialObjection_V7_GoalOriented")
    agent = CallFlowAgent(initial_state=initial_state)

    agent.session = MagicMock()
    agent.session.userdata = initial_state
    agent.session.say = AsyncMock()
    agent.on_enter = AsyncMock()
    agent._speak_and_log_utterance = AsyncMock(return_value=True)

    # 2. Stimulus
    user_response = "I'm still not interested."

    await agent.on_user_turn_completed(turn_ctx=None, new_message=MagicMock(content=user_response))

    # 3. Assertion
    assert agent.session.userdata.current_node_id == "N_Obj_EarlyDismiss_DirectValueChallenge_V9_EscalationEnabled"


@pytest.mark.asyncio
@patch('caller_agent.KBProcessor')
async def test_partner_availability_unsure_transition(MockKBProcessor):
    """
    Tests that if the user expresses uncertainty in the N018 node,
    the agent correctly transitions to the node for suggesting a partner check.
    """
    # 1. Setup
    initial_state = CallFlowState(current_node_id="N018_ConfirmPartnerAvailability")
    agent = CallFlowAgent(initial_state=initial_state)
    agent.session = MagicMock()
    agent.session.userdata = initial_state
    agent.session.say = AsyncMock()
    agent.on_enter = AsyncMock()
    agent._speak_and_log_utterance = AsyncMock(return_value=True)

    # 2. Stimulus
    user_response = "I don't know, I'll have to check with them."

    await agent.on_user_turn_completed(turn_ctx=None, new_message=MagicMock(content=user_response))

    # 3. Assertion
    assert agent.session.userdata.current_node_id == "N017D_SuggestPartnerCheck_ScheduleFollowUpCall"


@pytest.mark.asyncio
@patch('caller_agent.KBProcessor')
async def test_suggest_partner_check_speaks_correct_script(MockKBProcessor):
    """
    Tests that the agent speaks the corrected script for the N017D node.
    """
    # 1. Setup
    initial_state = CallFlowState(current_node_id="N017D_SuggestPartnerCheck_ScheduleFollowUpCall")
    agent = CallFlowAgent(initial_state=initial_state)
    agent.session = MagicMock()
    agent.session.userdata = initial_state
    agent.session.say = AsyncMock()
    agent._speak_and_log_utterance = AsyncMock(return_value=True)

    # 2. Stimulus
    await agent.on_enter()

    # 3. Assertion
    agent._speak_and_log_utterance.assert_called_once()
    spoken_text = agent._speak_and_log_utterance.call_args[0][0]
    expected_script = "No problem. Why don't you check with them and see what time works best? I can give you a quick call back tomorrow to lock it in. Does that sound fair?"
    assert spoken_text == expected_script
