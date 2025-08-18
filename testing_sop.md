# Testing Strategy and SOP

Purpose
- Establish a repeatable, strict testing process for the call-flow agent aligned with zero-exit policy, anti-repetition, strict goal gating, and contextual bridging.
- Provide a single reference to create, run, and evaluate per-node tests and the end-to-end scenario.

Test Policy (Authoritative)
- Zero exits anywhere: agent must persist and progress; do not let off mid-flow.
- Anti-repetition strict:
  - Fail on exact sentence duplication across turns and within a single turn.
  - Fail on near-duplicates using 6-gram similarity across the entire conversation history and within-turn sentences (Jaccard & contiguous reuse).
- Strict goal gating: do not transition until the current node’s goal is verifiably achieved.
- Contextual bridge required: after objections or Q&A detours, the next line must acknowledge and smoothly resume the node goal.
- End-to-end success: appointment booked + explicit homework video commitment.

Source of Truth for Nodes and Transitions
- complete_conversation_script.md
- Tracking artifact: nodes_master_checklist.md

SOP Overview
1) Select next node to test
   - Open nodes_master_checklist.md
   - Choose the first unchecked node in execution order.

2) Prepare test inputs
   - Create a per-node test module in test_pys/: test_node_<order>_<node_id>.py
   - Include realistic user utterances covering:
     - Normal path (no objection; clean goal achievement).
     - Objection raised then resolved; resume to goal.
     - Q&A detour then contextual bridge back to goal.
     - Failure probes:
       - Objection ignored.
       - Random/unrelated reply to objection.
       - Resolved objection but no resume to the node goal.
       - Early transition (goal not met).
       - Keeps handling objections when it should transition.
       - Abrupt, non-contextual resume.
       - Repeated phrase or near-duplicate phrase.

3) Run the harness (pytest)
   - Harness functions (to be implemented):
     - initialize_agent_at(node_id, seed): sets the agent state at the node under test.
     - step(user_text) -> TurnResult with fields:
       - agent_text: str
       - current_node: str
       - next_transition_target: str | None
       - node_goal_reached: bool
       - objection_detected: bool
       - kb_used: bool
     - get_history() -> List[str] of prior agent responses for anti-repetition checks.

4) Assertions (per test)
   - Behavior-level:
     - objection_detected expected True/False per script.
     - acknowledgment present for objections; KB splice used when policy requires (if enabled).
   - State-level:
     - node_goal_reached aligns with transition decisions.
     - No transition until node_goal_reached == True.
     - Once node_goal_reached == True, transition to correct next node immediately.
   - Output-level:
     - assert_no_repeat: exact + 6-gram near-duplicate checks across history and within the turn.
     - assert_contextual_bridge: after objections/detours, the first sentence acknowledges the last user content before resuming the node goal.
     - assert_goal_met_for_node: node-specific: surface minimal success signals that satisfy the node’s MVP goal.
     - assert_transition_correct: transition target matches canonical next node(s) for the scenario.

5) Evaluate results and report
   - On failure, produce a structured report (see template below).
   - Do not change runtime code in the same pass; provide the report to the owner.
   - After fixes are applied, rerun tests and update nodes_master_checklist.md.

Anti-Repetition Validator (Rules)
- Sentence-level:
  - Normalize: lowercase, trim, collapse whitespace.
  - Compare each sentence against:
    - All prior agent sentences in the conversation.
    - Other sentences within the current response.
- Near-duplicate (6-gram):
  - Tokenize words; generate 6-grams.
  - Compute Jaccard overlap with the union of prior agent 6-grams; FAIL if > 0.6.
  - Also flag contiguous 6-gram reuse across consecutive turns.
- Bridge/acknowledgment variation:
  - Dedicate the first sentence after objection as a bridge; ensure it is not a repeat or near-duplicate of prior bridge/ack statements in the same node session.

Contextual Bridge Validator (Rules)
- The first sentence after an objection or Q&A detour must:
  - Acknowledge the user’s point concisely (keyword overlap with last user utterance or objection label reference).
  - Then re-aim at the node’s MVP goal in the second sentence or clause.
- Fails if the agent jumps directly to script without acknowledging the last user context.

Goal Gating Validator (Rules)
- Define per-node minimal “goal satisfied” criteria (node MVP signals). Examples:
  - IntroduceModel: clear concise summary + open-ended prompt for concerns.
  - KB_QA: direct answer + value framing question delivered.
  - IncomeBackground: employment status captured and routed.
  - FinancialQualification: capital/credit path decided; next node consistent with the terminal condition.
  - Commitment: verbal commitment confirmed.
  - Scheduling: timezone captured, time range, concrete time selection, Zoom confirmation.
  - Finalization: confirmation text “Confirmed, I’ll see you there”; homework video “Got it” reply and explicit commitment to watch.
- A transition is only valid if the node’s MVP signals are satisfied.

Per-Node Test Template (Pattern)
- File name: test_pys/test_node_<order>_<node_id>.py
- Tests to include at minimum:
  - test_objection_then_resume_smoothly_pass
  - test_objection_ignored_fail
  - test_random_unrelated_reply_fail
  - test_resolved_but_no_resume_fail
  - test_qna_detour_then_resume_pass
  - test_early_transition_fail
  - test_correct_transition_after_goal_pass
  - test_no_repetition_under_rotation
  - test_multi_objection_chain_transitions_cleanly  # NEW: chain multiple objections across nodes
  - test_varied_objection_categories_without_repetition  # NEW: cover not_interested, no_time, no_recall, callback_request
- Each test:
  - Initialize at node with seed thread_id for determinism.
  - Provide user utterances.
  - Call step() sequentially; run validators per turn; assert final node_goal_reached and transition correctness.

Multi-Objection, Multi-Intent Chain (Required)
- Purpose: ensure agent can handle multiple distinct objections in sequence without repeating pivots and still transition correctly.
- Pattern (example opener → IntroduceModel chain):
  1) Start at N_Opener_StackingIncomeHook_V3_CreativeTactic
     - User A: “Not really.” (general_disinterest)
     - Assert: transition to IntroduceModel; assert_no_exit; assert_bridge_and_pivot or assert_human_like_pivot; assert_no_repeat vs history.
  2) At N_IntroduceModel_And_AskQuestions_V3_Adaptive
     - User B: “Just don’t have the time right now.” (time_busy/no_time)
     - Assert: OBVM/human-like checks pass; assert_no_repeat across both pivots; correct next transition.
  3) Optional third objection at IntroduceModel (e.g., no_recall)
     - Assert same invariants; confirm transitions and anti-repetition across all prior turns.
- Validators to apply each turn:
  - assert_no_exit
  - assert_bridge_and_pivot OR assert_human_like_pivot (see below)
  - assert_no_repeat(history_before, last_agent_text)
  - assert_disc_tone(text, persona='S' for opener)

Human-Like Pivot Validator (Authoritative Usage)
- Always run for opener objections; for non-opener when pivot tokens appear or OBVM assert is inconclusive.
- Checks:
  - Denylist awkward collocations (e.g., “bottom line—back to the outcome that moves revenue”, “quick pivot—back to …”).
  - Discourse-marker chaining ban: if starts with “Bottom line” or “Quick pivot”, do not allow “back to/returning/pivot to” within first 5 tokens.
  - Finite/action verb required.
  - Concreteness to node goal keywords OR a micro-ask OR explicit resume cue:
    - IntroduceModel concrete terms: website, websites, set up, explain, model, why, how.
    - Explicit resume examples: “let’s get back …”, “back to the next step”.
  - Context anchor overlap with user text or objection label vocabulary.
  - Functional next-step cue when pivot tokens are present (question mark, “let’s…”, “I’ll…”, “here’s…”).
- Implementation reference:
  - tests/harness/agent_test_harness.py -> assert_human_like_pivot()

Varied Objection Categories Coverage (Required)
- For opener-family nodes, parameterize tests across categories:
  - not_interested, no_time, no_recall, callback_request (from fixtures).
- For each, assert:
  - Transition key exists AND result.next_node equals nodes[current].transitions[key].
  - assert_no_exit(), assert_no_repeat().
  - assert_bridge_and_pivot() OR assert_human_like_pivot().
  - assert_disc_tone(text, 'S') for opener pivots.

Rotation Anti-Repetition (Required)
- Trigger the same objection label twice (with a neutral turn between) to ensure fresh pivots:
  - Assert jaccard 6-gram distance <= threshold (fail if too similar).
  - Confirm bank rotation or generator variants produce non-near-duplicate outputs.

End-to-End Chain Insertion
- Insert at least one multi-objection chain in the E2E SOP:
  - At opener: disinterest
  - At IntroduceModel: time_busy
  - Later nodes: one more distinct objection (e.g., cost/capital concern)
- At each step, apply human-like pivot validator and anti-repetition checks; assert successful transitions and maintenance of policy caps (3+1).

End-to-End Test SOP
- Scenario: from opener through N_Finalize_And_EndCall_V1_Adaptive.
- Include a sequence of diverse objections across the flow to stress the objection engine. Example objection ladder:
  1. Trust/Scam concern (risk/credibility)
  2. Time constraint (real busy)
  3. Value skepticism (why listen)
  4. No recall of ad
  5. Cost/capital concern
  6. Process/technical question detour
  7. Scheduling friction (partner/availability)
- Requirements:
  - At each objection, the agent must acknowledge, avoid repetition, and bridge back to the node MVP goal with fresh phrasing.
  - The agent must not exit; it must persist until node goals are satisfied and transitions are valid.
- Acceptance at end:
  - booking_confirmed == True (or equivalent state signal)
  - homework_commitment == True (explicit agreement + “Got it” reply)
  - No exits encountered; no loops; no early transitions.
  - No repeated or near-duplicate agent phrases.
  - All objections resolved with contextual bridges and continued progress.

Failure Report Template
- Node: <node_id>
- Test: <test_name>
- Seed/Thread: <id>
- User turn sequence: (list)
- Agent outputs: (list)
- Failure reasons:
  - [ ] Objection ignored
  - [ ] Random/unrelated reply
  - [ ] Resolved objection but no resume to node goal
  - [ ] Early transition before goal
  - [ ] Kept handling instead of transitioning when goal done
  - [ ] Abrupt non-contextual resume (bridge missing)
  - [ ] Repetition detected (exact / near-duplicate)
  - [ ] Goal not satisfied but transition attempted
  - [ ] Incorrect next node target
- Evidence:
  - Last user utterance
  - Agent line(s) violating rule
  - Validator diffs (for n-gram overlap, bridge failure)
- Suggested fix focus:
  - Angle or pivot bank
  - Bridge template variation
  - Goal satisfaction criteria wiring
  - Transition condition phrasing/logic

Execution Cadence
- Create test module for one node at a time.
- Run tests and produce a failure report if any assertion fails.
- Await owner’s fix; rerun and verify.
- Check off the node in nodes_master_checklist.md.
- Proceed sequentially until all nodes pass, then run end-to-end.

Versioning and Traceability
- Keep seeds fixed per test to ensure determinism.
- Include test names and seeds in reports.
- Update nodes_master_checklist.md with date and status notes after each node is validated.

Appendix: Human-Like Pivot Playbook (Common Solutions)
- If tests fail due to robotic/awkward pivots:
  1) Patch source banks in objection_handler (MVP_GOALS pivot_bank) to remove awkward collocations.
  2) Keep denylist up to date in assert_human_like_pivot (tests/harness/agent_test_harness.py).
  3) Ensure finalize_agent_text shaping doesn’t stitch multiple discourse markers (“Bottom line” + “back to”).
  4) Allow explicit resume cues (e.g., “let’s get back…”) as acceptable concreteness for IntroduceModel pivots.
  5) Add multi-objection chain tests to catch second-turn and third-turn pivots across nodes.

Notes
- No exits policy is enforced across all nodes and tests.
- If legal disclaimers require repetition, define an explicit whitelist with spacing rules and non-consecutive enforcement; default is zero repetition.

Common Failures and Canonical Fixes (Playbook)
- Legacy PSP leakage in opener objection responses
  - Symptom: Agent outputs verbose legacy paragraph (e.g., “I’m not just any student… Do you mind if I take 20 seconds…”), or tests that bypass runtime sinks pick up these lines directly from call_flow scripts.
  - Likely root causes:
    - Source-of-truth scripts in call_flow contain legacy text.
    - Integration/unit tests embed legacy strings directly.
    - Runtime sanitizers not reached because the harness bypasses handler/finalizer paths.
  - Fix steps (apply all):
    1) Source purge: Update call_flow nodes for opener objection families (e.g., N_Obj_EarlyDismiss_AskShareBackground_V7) to a canonical compliant line including a pivot token. Example: “No rush, I hear you. Let's get back to the next step.”
    2) Test/doc scrub: Replace embedded legacy strings in [tests/test_conversation_integration.py](tests/test_conversation_integration.py), [node_documentation.md](node_documentation.md), [complete_conversation_script.md](complete_conversation_script.md), and fixtures.
    3) Runtime guards: Keep composite kill-switches active in [objection_handler.enforce_pivot()](objection_handler.py:1) and [caller_agent.finalize_agent_text()](caller_agent.py:1) to remove legacy patterns defensively.
    4) Source-level assertions: Add a pytest that scans nodes' script fields for denylisted phrases so regressions fail fast even when sinks are bypassed.

- Opener OBVM invariant violations (missing S-tone, missing pivot, >3+1 sentences, pivot not last)
  - Symptom: assert_bridge_and_pivot(), sentence cap, or pivot-last tests fail.
  - Likely root causes:
    - Handler or finalizer not applying opener-specific shaping.
    - Script text lacks required tokens or uses >3 substantive sentences without pivot-last.
  - Fix steps:
    1) In [objection_handler.enforce_pivot()](objection_handler.py:1) and _enforce_opener_invariants(): ensure ack-first, S-tone “No rush,”, pivot presence, 3+1 cap, and pivot-last logic are enforced.
    2) In [caller_agent.finalize_agent_text()](caller_agent.py:1): reinforce opener-path shaping and 3+1 shaping; ensure opener node ID gating is correct.
    3) Update call_flow scripts for objection nodes to include an approved pivot token: one of ["let’s", "let's", "back to", "returning", "bottom line", "quick pivot", "let us"].

- Normal vs. objection path contamination
  - Symptom: Normal permission path carries S-tone/pivot shaping or objection validators fire on a normal transition.
  - Likely root cause: Global sanitizers not gated by node family + objection state.
  - Fix steps:
    1) Gate finalize_agent_text and opener sanitizers by both (is_opener_node && objection_detected).
    2) Add explicit tests for permission path: assert transition to permission_granted target and that objection shaping is NOT applied.

- TTS (external provider) flakiness impacting tests
  - Symptom: APIConnectionError, out-of-memory, or network failure causes test failures despite correct text/transition logic.
  - Fix steps:
    1) Introduce a test-mode configuration to stub or disable TTS during tests.
    2) Ensure tests assert on text/transition only; never rely on audio frames.

- Deterministic transition assertion gaps
  - Symptom: Tests pass without verifying the exact canonical next node.
  - Fix steps:
    1) Always assert both presence of the transition key on the current node and equality of result.next_node to nodes[current].transitions[key].

- Anti-repetition gaps
  - Symptom: Subtle near-duplicates slip through under rotation.
  - Fix steps:
    1) Strengthen assert_no_repeat to include 6-gram Jaccard and contiguous reuse checks across history and within-turn sentences.
    2) Maintain agent_utterance_history and compare pre/post step.

- Harness bypass of runtime sinks
  - Symptom: Sanitizers don’t run; tests pick up raw script text.
  - Fix steps:
    1) Keep runtime guards but ALSO assert source invariants on scripts.
    2) Prefer harness paths that exercise finalize_agent_text when validating shaping, but fail tests if source contains denylisted phrases.