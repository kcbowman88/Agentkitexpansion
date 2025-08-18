import logging
from dataclasses import dataclass, field
from typing import Optional, Type, Any
from enum import Enum
import time
import asyncio # Ensure asyncio is imported
import re
import random

from livekit.agents import Agent, function_tool, RunContext, llm
from call_flow import CALL_FLOW
# Provide a patchable proxy for CALL_FLOW to satisfy tests that patch caller_agent.nodes.get
class _NodesProxy:
    def __init__(self, backing):
        self._backing = backing
    def get(self, key, default=None):
        try:
            return self._backing.get(key) if default is None else self._backing.get(key, default)
        except Exception:
            return None
# Wrap imported CALL_FLOW dict
nodes = _NodesProxy(CALL_FLOW)
from global_prompt import GLOBAL_PROMPT
from transition_evaluator import TransitionEvaluator
from disc_classifier import DISCClassifier, DISCProfile
from generative_objection_handler import (
    generate_objection_response,
    GenerativeObjectionContext,
    ResponseOrchestrator
)
from state_manager import CallFlowState
from conversation_state_manager import ConversationStateManager, StrategyType
from node_script_tracker import NodeScriptTracker
from tactical_responder import TacticalResponder
from ab_testing import ab_test_manager
from analytics import conversation_analytics
from kb_processor import KBProcessor, get_concise_snippet
import yaml
from pivot_controller import pivot_controller

# --- Configuration Flags ---
RESPONSE_FINALIZER_ENABLED = True
DEBUG_VALIDATORS = False
USE_GENERATIVE_OBJECTION_HANDLER = True

# --- Constants for Sanitization ---
FINALIZER_DENYLIST = [
    "one quick line", "under 25 seconds", "as a language model",
    "i cannot", "i'm just an ai", "not interested", "no thanks",
    "maybe later", "stop calling", "unsubscribe"
]
KB_TEMPLATE_ARTIFACT_TERMS = [
    "works cited", "references:", "bibliography", "citations",
    "now, answer the user’s question directly", "now, answer the user's question directly",
    "answer:", "final answer:", "reference:", "source:"
]
KB_URL_LIKE_PATTERN = r"(?:https?://|www\.)\S+"

# --- Helper Functions ---
def _sentence_split(text: str) -> list:
    return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

def _shingles(s: str, n: int = 6) -> set:
    tokens = s.lower().split()
    if len(tokens) < n:
        return set([" ".join(tokens)]) if tokens else set()
    return set([" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)])

def _jaccard(a: str, b: str, n: int = 6) -> float:
    sa, sb = _shingles(a, n), _shingles(b, n)
    if not sa and not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb) or 1
    return inter / union

def _sanitize_kb_template_artifacts(text: str) -> str:
    t = (text or "").strip()
    for term in KB_TEMPLATE_ARTIFACT_TERMS:
        t = t.replace(term, "")
    t = re.sub(KB_URL_LIKE_PATTERN, "", t).strip()
    return re.sub(r"\s{2,}", " ", t).strip() or "Let's keep moving."

def finalize_agent_text(state, text: str, *, is_objection: bool = False) -> str:
    """
    Enforce denylist and anti-repetition checks. Avoids destructive rewriting of generative responses.
    Updates state.agent_utterance_history upon acceptance.
    """
    try:
        if not RESPONSE_FINALIZER_ENABLED:
            if isinstance(getattr(state, "agent_utterance_history", None), list):
                state.agent_utterance_history.append(text)
            return text

        t = (text or "").strip()
        t = _sanitize_kb_template_artifacts(t)
        # Safety: scrub unresolved template placeholders (e.g., "{income_amount}")
        try:
            t = t.replace("{income_amount}", "$20k")
            t = re.sub(r"\{[^}]+\}", "", t)
        except Exception:
            pass
        tl = t.lower()

        if any(term in tl for term in FINALIZER_DENYLIST):
            logging.warning(f"Finalizer: Denylist triggered. Overriding response. Original: '{text}'")
            t = "Understood. Let's continue."

        # history = getattr(state, "agent_utterance_history", []) or []
        # if history:
        #     last_utterance = history[-1]
        #     if tl == last_utterance.lower():
        #         logging.warning(f"Finalizer: Exact repetition detected. Overriding response. Original: '{text}')")
        #         t = "Got it. Moving forward."
        #     elif _jaccard(t, last_utterance, n=6) > 0.7:
        #         logging.warning(f"Finalizer: Near-repetition detected. Overriding response. Original: '{text}')")
        #         t = "Understood. Let's keep the momentum."

        if not t:
            t = "Let’s keep moving."

        if isinstance(getattr(state, "agent_utterance_history", None), list):
            state.agent_utterance_history.append(t)

        if DEBUG_VALIDATORS:
            logging.debug(f"FINALIZER_OUT: {t}")

        return t
    except Exception as e:
        logging.error(f"finalize_agent_text error: {e}", exc_info=True)
        if isinstance(getattr(state, "agent_utterance_history", None), list):
            state.agent_utterance_history.append(text)
        return text

# ScriptSanitizer removed


# --- The Unified Call Flow Agent ---
class CallFlowAgent(Agent):
    def __init__(self, initial_state: CallFlowState, instructions: str = ""):
        super().__init__(instructions=instructions)
        self.disc_classifier = DISCClassifier()
        self.kb_processor = KBProcessor()
        self.conversation_state_manager = ConversationStateManager()
        self.response_orchestrator = ResponseOrchestrator(initial_state, self.conversation_state_manager, self.kb_processor)
        self.script_tracker = NodeScriptTracker()
        self._session = None
        logging.info("CallFlowAgent initialized with new, simplified logic.")
        
    @property
    def session(self):
        return self._session
    
    @session.setter
    def session(self, value):
        self._session = value

    async def _safe_say(self, text: str, state: CallFlowState) -> bool:
        """
        Low-level function to say text and detect interruptions.
        Does NOT log to history.
        Returns True if spoken completely, False if interrupted.
        """
        try:
            say_fn = getattr(self.session, "say", None)
            if not say_fn:
                logging.error("Session.say not available")
                return False
            
            # Register every bot utterance for pivot tracking
            pivot_controller.register_bot_utterance(text, state.current_node_id)
            
            await say_fn(text, allow_interruptions=True)
            return True
        except asyncio.CancelledError:
            self.conversation_state_manager.set_flag("last_agent_interrupted", True)
            logging.warning(f"Agent interrupted while saying: '{text}'")
            return False
        except Exception as e:
            logging.error(f"Low-level _safe_say error: {e}", exc_info=True)
            return False

    def _enforce_final_turn_compliance(self, state, text: str, node_data: dict, will_transition: bool = False) -> str:
        """
        Guardrail: ensure final agent turn complies with style rules.
        For responses generated by ResponseOrchestrator, trust its output for conciseness and pivoting.
        Only apply basic cleanup and ensure it ends with a question if not transitioning.
        """
        try:
            t = (text or "").strip()

            # If the response is from the generative orchestrator and already ends with a question,
            # or if we are transitioning, trust its formatting.
            # The orchestrator is responsible for Rule 4 (concise, ends with question) and Rule 5 (pivot).
            if USE_GENERATIVE_OBJECTION_HANDLER and t.endswith("?"):
                # Just ensure it's clean and return as is
                return t
            
            # For other cases (e.g., hardcoded scripts, or if generative handler didn't end with a question)
            # apply the original compliance logic.
            if not will_transition and not t.endswith("?"):
                node_id = (node_data or {}).get("id") or ""
                if node_id.startswith("N_IntroduceModel"):
                    q = " What questions come to mind?"
                elif node_id.startswith("N_KB_Q&A"):
                    q = " Does that make sense so far?"
                else:
                    q = " Does that make sense?"
                t = (t.rstrip(".") + q).strip()

            # Remove aggressive sentence truncation, as generative model should handle conciseness
            # sents = _sentence_split(t)
            # if len(sents) > 3:
            #     t = ". ".join(sents[:2]).rstrip(".")
            #     if not will_transition and not t.endswith("?"):
            #         t = t + "?"
            return t
        except Exception:
            return text

    def _analyze_sentiment(self, text: str) -> float:
        positive_words = ["good", "great", "excellent", "amazing", "interested", "curious", "happy", "excited"]
        negative_words = ["bad", "terrible", "awful", "hate", "dislike", "not interested", "sad", "frustrated"]
        
        text_lower = text.lower()
        
        # Word-based analysis
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Simple negation handling
        if "not" in text_lower and "happy" in text_lower:
            negative_count += 1
            positive_count -=1
        if "not" in text_lower and "great" in text_lower:
            negative_count += 1
            positive_count -=1

        if "but" in text_lower:
            # If 'but' is present, it often signals a mixed sentiment.
            # We can neutralize the score slightly towards zero.
            return 0.0

        total_emotional_words = positive_count + negative_count
        if total_emotional_words == 0:
            return 0.0
            
        score = (positive_count - negative_count) / total_emotional_words
        return max(-1.0, min(1.0, score))

    def _is_ambiguous(self, text: str) -> bool:
        """
        Minimal ambiguity detector used by unit tests.
        Treats short acknowledgements and backchannels as ambiguous.
        """
        try:
            t = (text or "").strip().lower()
            if not t:
                return True
            tokens = {
                "yeah", "yep", "uh-huh", "uh huh", "huh", "hmm", "mm", "mmm", "uh", "um"
            }
            return t in tokens
        except Exception:
            return True

    # This method has been entirely removed as it is now obsolete.

    def _is_company_intent(self, user_input: str, state) -> bool:
        """
        Back-compatibility seam for tests that patch this method to force KB path.
        Default behavior: False (do not trigger inline KB).
        """
        return False

    def _generate_dynamic_kb_qa_script(self, user_input: str, state) -> str:
        """
        Back-compatibility seam for tests that patch this method to return a KB answer.
        Default behavior: empty string.
        """
        return ""

    async def _speak_and_log_utterance(self, utterance: str, state: CallFlowState, is_objection: bool = False) -> bool:
        """
        Speaks a single, complete utterance, handles interruptions, and logs to history.
        Returns True if spoken completely, False otherwise.
        """
        processed_utterance = utterance
        if state.customer_name:
            processed_utterance = processed_utterance.replace("{{customer_name}}", state.customer_name)

        final_utterance = finalize_agent_text(state, processed_utterance, is_objection=is_objection)
        
        if not final_utterance:
            return True

        interrupted = False
        spoken_completely = await self._safe_say(final_utterance, state)
        if not spoken_completely:
            interrupted = True

        self.conversation_state_manager.add_turn(
            speaker='agent',
            utterance=final_utterance,
            node_id=state.current_node_id,
            interrupted=interrupted
        )
        logging.info(f"Agent {'interrupted while saying' if interrupted else 'said'}: '{final_utterance}'")
        return not interrupted

    async def _speak_node_script(self, state: CallFlowState):
        """
        Speaks the registered script for the current node, segment by segment.
        """
        node_id = state.current_node_id
        while True:
            segment_index, segment_text = self.script_tracker.get_next_segment(node_id)
            if segment_text is None:
                break # Script is done or not registered

            spoken_completely = await self._speak_and_log_utterance(segment_text, state)
            if spoken_completely:
                self.script_tracker.mark_segment_spoken(node_id, segment_index)
            else:
                # Interrupted
                break
    
    async def on_enter(self, suppress_script: bool = False):
        try:
            state: CallFlowState = self.session.userdata
            current_node = nodes.get(state.current_node_id)
            if not current_node:
                logging.error(f"Node '{state.current_node_id}' not found. Closing session.")
                await self.session.close()
                return

            logging.info(f"Entering node: {state.current_node_id}")

            if suppress_script:
                logging.info(f"Script suppressed for node {state.current_node_id} by transition directive.")
                return

            if self.script_tracker.should_speak_script(state.current_node_id):
                speak_script_segments = current_node.get("speak_script", [])
                if speak_script_segments and isinstance(speak_script_segments, list):
                    self.script_tracker.register_script(state.current_node_id, speak_script_segments)
                    await self._speak_node_script(state)
                else:
                    logging.info(f"Node {state.current_node_id} has empty or no speak_script; not speaking on enter.")
            else:
                # This part for alternative responses can be refactored or removed
                # depending on the desired behavior for revisited nodes.
                logging.info(f"Script for node {state.current_node_id} already completed.")

        except Exception as e:
            logging.error(f"Error in on_enter: {e}", exc_info=True)

    async def on_user_turn_completed(self, turn_ctx: llm.ChatContext, new_message: llm.ChatMessage) -> None:
        try:
            user_input = str(new_message.content) if new_message.content else ""
            logging.debug(f"on_user_turn_completed: Received user input: '{user_input}'")
            if not user_input:
                logging.warning("No user input received.")
                return

            state: CallFlowState = self.session.userdata
            
            was_interrupted = self.conversation_state_manager.pop_flag("last_agent_interrupted", False)

            if was_interrupted:
                logging.info("Previous agent utterance was interrupted. Handling interruption.")
                await self._handle_interruption(user_input, state)
            else:
                await self._handle_user_response(user_input, state)
        except Exception as e:
            logging.error(f"Error in on_user_turn_completed: {e}", exc_info=True)

    async def _handle_interruption(self, user_input: str, state: CallFlowState):
        """
        Handles cases where the user interrupts the agent using the
        Adaptive Two-Turn Interruption Engine.
        """
        logging.info(f"Handling interruption with Adaptive Engine. User input: '{user_input}'")
        state.interruption_count += 1

        # TURN 1: DIAGNOSE, ADAPT, & RESPOND
        # 1. Analyze the interruption
        # TODO: Add logic to analyze interruption intent

        # 2. Analyze the user's behavioral style
        if not state.disc_profile:
            state.disc_profile = self.disc_classifier.classify(user_input)
            logging.info(f"Classified user DISC profile as: {state.disc_profile.name}")

        # 3. Choose a tool (KB lookup or generative response)
        current_node_id = state.current_node_id
        if current_node_id not in state.tactic_history:
            state.tactic_history[current_node_id] = []

        # One-Shot Tactic Logic
        if state.interruption_count > 1 and len(state.tactic_history[current_node_id]) > 0:
             logging.info("One-shot tactic exhausted. Escalating to global objection handler.")
             # TODO: Implement escalation to global objection handler
             await self._handle_user_response(user_input, state) # Placeholder
             return

        kb_result = self.kb_processor.search(user_input)
        if kb_result:
            logging.info("Found relevant information in KB.")
            state.tactic_history[current_node_id].append("kb_search")
            await self._speak_and_log_utterance(kb_result, state, is_objection=True)
            return

        # Fallback to the generative response if KB has no answer
        logging.info("No KB result. Using generative response for interruption.")
        state.tactic_history[current_node_id].append("generative_response")
        await self._handle_user_response(user_input, state)

    async def _resume_script(self, state: CallFlowState):
        """
        Resumes speaking the script from where it was interrupted.
        """
        logging.info(f"Attempting to resume script for node {state.current_node_id}")
        await self._speak_node_script(state)

    async def _handle_user_response(self, user_input: str, state: CallFlowState):
        """
        Orchestrates the response to user input by first checking for deterministic transitions,
        then falling back to the generative ResponseOrchestrator.
        """
        try:
            logging.debug(f"Processing user input: '{user_input}' in node '{state.current_node_id}'")
            self.conversation_state_manager.add_turn('user', user_input, state.current_node_id)

            # --- Special Handling for Data-Capture Nodes ---
            if state.current_node_id == "N201A_Employed_AskYearlyIncome_V8_Adaptive":
                try:
                    # Extract numbers from the user's response to capture income
                    income_numbers = re.findall(r'\d{1,3}(?:,\d{3})*|\d+', user_input)
                    if income_numbers:
                        # Convert to float and handle thousands (e.g., "50k")
                        income_str = income_numbers[0].replace(',', '')
                        if 'k' in user_input.lower():
                            income_value = float(income_str) * 1000
                        else:
                            income_value = float(income_str)
                        state.user_income = income_value
                        logging.info(f"Captured user income: {state.user_income}")
                except (ValueError, IndexError) as e:
                    logging.warning(f"Could not parse income from user input: '{user_input}'. Error: {e}")


            # --- Special Handling for Logical Nodes ---
            if state.current_node_id == "Logic_Split_Node_Financial_Qualification":
                logging.info("Entering logical node: Logic_Split_Node_Financial_Qualification")
                node_data = nodes.get(state.current_node_id, {})
                transitions = node_data.get("transitions", [])

                high_income_target = next((t['target'] for t in transitions if t.get('condition') == 'high_income'), None)
                standard_income_target = next((t['target'] for t in transitions if t.get('condition') == 'standard_income'), None)

                if not high_income_target or not standard_income_target:
                    logging.error("Could not find valid high_income/standard_income transitions. Halting.")
                    # Optionally, transition to an error-handling node
                    # await self._transition_to_node("N_EndCall_Technical_Issue")
                    # await self.on_enter()
                    return

                # Check if user_income has been set
                if state.user_income is not None:
                    if state.user_income >= 40000:
                        logging.info(f"User income ({state.user_income}) is >= $40,000. Transitioning to high_income path.")
                        chosen_target = high_income_target
                    else:
                        logging.info(f"User income ({state.user_income}) is < $40,000. Transitioning to standard_income path.")
                        chosen_target = standard_income_target
                else:
                    # Fallback if income was not captured for some reason
                    logging.warning("User income not found in state. Defaulting to standard_income path.")
                    chosen_target = standard_income_target

                await self._transition_to_node(chosen_target)
                await self.on_enter()
                return

            current_node = nodes.get(state.current_node_id)
            if not current_node:
                logging.error(f"Node '{state.current_node_id}' not found in CALL_FLOW.")
                await self._transition_to_node("N_EndCall_Technical_Issue")
                return

            # 1. Check for deterministic transitions first
            transitions = current_node.get("transitions", [])
            if transitions:
                evaluator = TransitionEvaluator(state)

                # Convert list of transitions to a dictionary for the evaluator
                transition_conditions = {t.get("condition"): t.get("target") for t in transitions}

                # Use the evaluator to find the first matching transition
                condition_met, target_node_id, condition_desc = evaluator.evaluate_response(user_input, transition_conditions)

                if condition_met:
                    logging.info(f"Deterministic transition triggered: '{condition_desc}' -> '{target_node_id}'")
                    await self._transition_to_node(target_node_id, suppress_script=False)
                    await self.on_enter(suppress_script=False)
                    return

            # 2. If no deterministic transition, use the ResponseOrchestrator
            logging.info(f"No deterministic transition found. Delegating to ResponseOrchestrator.")
            
            node_data = {
                'id': state.current_node_id,
                'goal': current_node.get('goal', ''),
                'transitions': transitions,
            }

            result = self.response_orchestrator.generate_response(user_input, node_data)
            logging.info(f"ResponseOrchestrator result: {result}")

            response_text = result.get('response', "")
            target_node = result.get('target_node')
            should_transition = result.get('should_transition', False)

            spoken_text = ""
            if response_text:
                spoken_completely = await self._speak_and_log_utterance(response_text, state, is_objection=True)
                if not spoken_completely:
                    logging.warning("Agent interrupted speaking response from orchestrator. Halting action.")
                    return
                spoken_text = response_text

            # 3. Handle post-response actions (e.g., transitions from orchestrator)
            if should_transition and target_node:
                response_ends_with_question = spoken_text.strip().endswith('?')
                silent_transition_nodes = ["N_KB_Q&A_With_StrategicNarrative_V3_Adaptive"]
                
                # Strict Speak-Then-Listen Gating logic
                if response_ends_with_question and target_node not in silent_transition_nodes:
                    logging.info(f"Agent asked a question ('{spoken_text}'). Delaying transition to await user response.")
                    state.waiting_for_objection_response = True
                else:
                    # Proceed with the transition.
                    # Suppress the next node's script *only if* we actually spoke a non-empty response.
                    suppress_next_script = bool(spoken_text)
                    await self._transition_to_node(target_node, suppress_script=suppress_next_script)
                    # If the transition is not delayed, we need to enter the new node now.
                    await self.on_enter(suppress_script=suppress_next_script)
            else:
                logging.info("Orchestrator did not direct a transition or retry. Agent remains in the current node.")

        except Exception as e:
            logging.error(f"CRITICAL: Unhandled error in _handle_user_response: {e}", exc_info=True)
            await self._speak_and_log_utterance("I've run into an issue. Let's try that again.", state)

    async def _transition_to_node(self, next_node_id: str, suppress_script: bool = False):
        try:
            state: CallFlowState = self.session.userdata
            logging.info(f"Attempting to transition to node: {next_node_id}")
            
            # Reset pivot state on node changes to prevent multi-pivot loops
            try:
                pivot_controller.reset_on_transition(next_node_id)
            except Exception:
                logging.debug("PivotController.reset_on_transition failed", exc_info=True)
            
            # Set the suppress_next_node_script flag in conversation_state_manager
            # This flag is popped by on_enter of the *next* node.
            if suppress_script:
                self.conversation_state_manager.set_flag('suppress_next_node_script', True)
                logging.info(f"Set suppress_next_node_script flag for next node ({next_node_id}).")
            else:
                # Ensure the flag is cleared if we are explicitly NOT suppressing
                self.conversation_state_manager.set_flag('suppress_next_node_script', False)
                logging.info(f"Cleared suppress_next_node_script flag for next node ({next_node_id}).")

            state.current_node_id = next_node_id
            # self.session.clear_user_turn() # This should be handled by the agent loop, not here.
        except Exception as e:
            logging.error(f"Unexpected error in _transition_to_node: {e}", exc_info=True)

# Back-compat alias for legacy tests expecting `CallerAgent`
CallerAgent = CallFlowAgent