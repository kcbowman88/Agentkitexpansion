# Test Cases for State Machine Fixes

## 1. Skipping Turns Test
**Objective**: Verify that the conversation follows a strict turn-based flow without skipping.

**Test Steps**:
1. Start the conversation
2. While the agent is speaking, try to provide user input
3. Verify that the input is not processed until the agent finishes speaking

**Expected Result**: The agent should complete its turn before processing any user input.

## 2. Non-Stock Responses Test
**Objective**: Verify that the system handles unrecognized responses gracefully.

**Test Steps**:
1. Start the conversation
2. Provide a response that doesn't match any predefined transition categories (e.g., "blargh", "xyz", "I like turtles")
3. Verify that the system uses the default transition or a fallback mechanism

**Expected Result**: The system should not crash and should continue the conversation using a default or fallback transition.

## 3. "I'm Busy" Objection Test
**Objective**: Verify that the "I'm busy" objection is handled correctly.

**Test Steps**:
1. Start the conversation
2. When prompted, respond with "I'm busy" or "I don't have time"
3. Verify that the system transitions to the appropriate node for handling time-based objections

**Expected Result**: The system should transition to `N_Obj_RealBusy_BluntCheck_V3_Adaptive` and follow the correct flow for handling time-based objections.

## 4. "Not Interested" Objection Test
**Objective**: Verify that the "not interested" objection is handled correctly.

**Test Steps**:
1. Start the conversation
2. When prompted, respond with "I'm not interested" or "This isn't for me"
3. Verify that the system transitions to the appropriate node for handling interest-based objections

**Expected Result**: The system should transition to `N_Obj_EarlyDismiss_AskShareBackground_V7` and follow the correct flow for handling interest-based objections.

## 5. Ambiguous Responses Test
**Objective**: Verify that ambiguous responses are handled correctly.

**Test Steps**:
1. Start the conversation
2. Provide ambiguous responses like "huh", "what", "um", "well"
3. Verify that the system uses an appropriate fallback response

**Expected Result**: The system should provide a clarification response and continue the conversation.

## 6. Invalid State Transitions Test
**Objective**: Verify that invalid state transitions are handled gracefully.

**Test Steps**:
1. Modify the state machine to include an invalid transition
2. Trigger the invalid transition
3. Verify that the system handles the error gracefully

**Expected Result**: The system should log an error and either stay in the current state or fallback to a safe state.

## 7. Missing Node Test
**Objective**: Verify that missing nodes are handled gracefully.

**Test Steps**:
1. Modify the state machine to remove a node that is referenced in a transition
2. Trigger the transition to the missing node
3. Verify that the system handles the error gracefully

**Expected Result**: The system should log an error and either stay in the current state or fallback to a safe state.

## 8. Empty Response Test
**Objective**: Verify that empty responses are handled correctly.

**Test Steps**:
1. Start the conversation
2. Provide an empty response or silence
3. Verify that the system handles the response appropriately

**Expected Result**: The system should either prompt for a response again or use a default transition.