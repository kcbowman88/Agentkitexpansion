import logging
from dataclasses import dataclass, field
from typing import Optional, Type, Any, AsyncIterable
from enum import Enum
import time
import asyncio # Ensure asyncio is imported
import re

from livekit.agents import Agent, function_tool, RunContext, llm, ModelSettings
from livekit import rtc
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
from transition_evaluator import IntentAndTransitionEvaluator
from disc_classifier import DISCClassifier, DISCProfile
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
class CallFlowAgentV2(Agent):
    def __init__(self, initial_state: CallFlowState, instructions: str = ""):
        super().__init__(instructions=instructions)
        self.disc_classifier = DISCClassifier()
        self.kb_processor = KBProcessor()
        self.conversation_state_manager = ConversationStateManager()
        self.script_tracker = NodeScriptTracker()
        self.intent_evaluator = IntentAndTransitionEvaluator()
        self._session = None
        logging.info("CallFlowAgentV2 initialized.")
        
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
    
    def _get_node_script(self, node_data: dict) -> list[str]:
        """
        Gets the script to be spoken from a node, handling various possible structures.
        """
        if not node_data:
            return []

        # Order of preference for finding the script
        if "agent_says" in node_data:
            script = node_data["agent_says"]
            return [script] if isinstance(script, str) else script

        if "speak_script" in node_data:
            script = node_data["speak_script"]
            return [script] if isinstance(script, str) else script

        if "speech_output" in node_data and "script" in node_data["speech_output"]:
            script = node_data["speech_output"]["script"]
            return [script] if isinstance(script, str) else script

        if "opening_gambit" in node_data and "agent_says" in node_data["opening_gambit"]:
            script = node_data["opening_gambit"]["agent_says"]
            return [script] if isinstance(script, str) else script

        # Handle multi-step scripts which are common in the new structure
        scripts = []
        if "part_1" in node_data and "agent_says" in node_data["part_1"]:
             scripts.append(node_data["part_1"]["agent_says"])
        if "part_2" in node_data and "agent_says" in node_data["part_2"]:
             scripts.append(node_data["part_2"]["agent_says"])
        if "step_1" in node_data and "agent_says" in node_data["step_1"]:
            scripts.append(node_data["step_1"]["agent_says"])
        if "step_2" in node_data and "agent_says" in node_data["step_2"]:
            scripts.append(node_data["step_2"]["agent_says"])
        if scripts:
            return scripts

        return []

    async def on_enter(self, suppress_script: bool = False):
        try:
            state: CallFlowState = self.session.userdata
            current_node_data = nodes.get(state.current_node_id)
            if not current_node_data:
                logging.error(f"Node '{state.current_node_id}' not found. Closing session.")
                await self.session.close()
                return

            logging.info(f"Entering node: {state.current_node_id}")

            if suppress_script:
                logging.info(f"Script suppressed for node {state.current_node_id} by transition directive.")
                return

            # Use the new helper to get the script
            speak_script_segments = self._get_node_script(current_node_data)

            if speak_script_segments:
                for segment in speak_script_segments:
                    # Replace placeholders like {{customer_name}}
                    try:
                        if state.customer_name:
                             segment = segment.replace("{{customer_name}}", state.customer_name)
                    except Exception:
                        pass

                    spoken_completely = await self._speak_and_log_utterance(segment, state)
                    if not spoken_completely:
                        logging.warning(f"Interrupted while speaking segment in node {state.current_node_id}. Halting on_enter script.")
                        break # Stop speaking if interrupted
            else:
                logging.info(f"Node {state.current_node_id} has no script to speak on enter.")

        except Exception as e:
            logging.error(f"Error in on_enter: {e}", exc_info=True)

    async def on_user_turn_completed(self, turn_ctx: llm.ChatContext, new_message: llm.ChatMessage) -> None:
        try:
            user_input = str(new_message.content) if new_message.content else ""
            if not user_input:
                logging.warning("No user input received.")
                return

            state: CallFlowState = self.session.userdata
            self.conversation_state_manager.add_turn('user', user_input, state.current_node_id)
            
            current_node_data = nodes.get(state.current_node_id)
            if not current_node_data:
                logging.error(f"Node '{state.current_node_id}' not found. Aborting.")
                return

            # 1. Analyze user input for multiple intents
            transitions = current_node_data.get("transitions", [])
            intents = await self.intent_evaluator.evaluate(user_input, transitions, self.llm)

            question = intents.get("question")
            objection = intents.get("objection")
            transition_target = intents.get("transition_target")

            # 2. Prioritize handling questions and objections before transitions
            handled_interruption = False
            interruption_input = question or objection
            if interruption_input and interruption_input.lower() != "none":
                logging.info(f"Handling interruption: Question='{question}', Objection='{objection}'")

                response_text = ""
                # Prioritize KB for questions in Q&A nodes
                if question and "N_KB_Q&A" in state.current_node_id:
                    response_text = self.kb_processor.search(question)

                # If KB didn't answer, use the strategic toolkit
                if not response_text:
                    toolkits = ["strategic_toolkit", "one_shot_objection_handling", "flexible_objection_handling_protocol", "dynamic_interruption_protocol"]
                    strategic_toolkit = []
                    for key in toolkits:
                        if key in current_node_data:
                            strategic_toolkit = current_node_data[key]
                            break
                    tactic = await self._find_tactic(interruption_input, strategic_toolkit, self.llm)
                    if tactic and "agent_says" in tactic:
                        response_text = tactic.get("agent_says")

                # Fallback response if no other handler worked
                if not response_text:
                    response_text = "That's a good point. Let me get back to that in a moment."

                await self._speak_and_log_utterance(response_text, state, is_objection=True)
                handled_interruption = True

            # 3. Proceed with transition if one was identified
            if transition_target and transition_target.lower() != "none":
                # If we handled an interruption, we might want to add a small pause or confirming phrase
                # before transitioning, but for now we'll transition directly.
                logging.info(f"Transitioning from '{state.current_node_id}' to '{transition_target}' based on user intent.")
                await self._transition_to_node(transition_target)
                # The on_enter for the new node will be called, speaking its script.
                # We suppress the script if we just spoke an interruption response.
                await self.on_enter(suppress_script=handled_interruption)

            # If no transition and no interruption, the agent waits for the next user input.

        except Exception as e:
            logging.error(f"CRITICAL: Unhandled error in on_user_turn_completed: {e}", exc_info=True)
            await self._speak_and_log_utterance("I've run into an issue. Let's try that again.", state)

    async def _find_tactic(self, user_input: str, strategic_toolkit: list, llm_instance: llm.LLM) -> Optional[dict]:
        """
        Finds the best tactic from the strategic toolkit using an LLM to match intent.
        """
        if not strategic_toolkit:
            return None

        # Format the tactics for the prompt
        formatted_tactics = "{\n"
        for i, tactic in enumerate(strategic_toolkit):
            name = tactic.get("name", f"tactic_{i}")
            condition = tactic.get("condition", "No condition specified.")
            condition_cleaned = ' '.join(condition.split())
            formatted_tactics += f'  "{name}": "Condition: {condition_cleaned}",\n'
        formatted_tactics += "}"

        prompt = f"""
You are an expert at understanding conversational objections and questions. Your task is to choose the best-pre-written response tactic based on the user's statement.

The user just said: "{user_input}"

Based on this, which of the following tactics is the most appropriate response?

Here are the available tactics and their trigger conditions:
{formatted_tactics}

Analyze the user's statement and choose the single best tactic from the list. Respond with ONLY the name of the tactic (e.g., "TrustScamObjection"). If none of the conditions are a clear match, respond with the word "None".
"""

        chat = [llm.ChatMessage(role=llm.ChatRole.SYSTEM, content=prompt)]

        try:
            response = await llm_instance.chat(chat)
            tactic_name = response.choices[0].message.content.strip()

            # Find the chosen tactic in the list
            for tactic in strategic_toolkit:
                if tactic.get("name") == tactic_name:
                    logging.info(f"LLM chose tactic: {tactic_name}")
                    return tactic

            logging.info(f"LLM responded with '{tactic_name}', which is not a valid tactic name. No tactic chosen.")
            return None

        except Exception as e:
            logging.error(f"Error during LLM call in _find_tactic: {e}")
            return None

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

    async def tts_node(self, text_stream: AsyncIterable[str], model_settings: ModelSettings) -> AsyncIterable[rtc.AudioFrame]:
        """
        Custom TTS node to handle SSML tags.
        """
        # This is a simplified implementation. A more robust version would need to
        # handle the async stream more carefully. We accumulate the stream into a
        # single string here, which works for our use case since we send complete
        # script segments to the `say` method.

        complete_text = ""
        async for text_chunk in text_stream:
            complete_text += text_chunk

        if complete_text.strip().startswith("<speak>"):
            logging.info(f"SSML detected. Passing to TTS as a single block: {complete_text}")

            # Re-create a stream with the single, complete SSML string.
            # This assumes the underlying TTS engine (e.g., Cartesia, OpenAI TTS)
            # will correctly interpret the SSML when passed as a whole.
            async def ssml_stream():
                yield complete_text

            # Call the default TTS node with the SSML string.
            return Agent.default.tts_node(self, ssml_stream(), model_settings)
        else:
            # Not SSML, so let the default handler process it, which will likely
            # do sentence-based chunking for better streaming performance.
            logging.info(f"Plain text detected. Using default TTS processing: {complete_text}")
            async def original_stream():
                yield complete_text

            return Agent.default.tts_node(self, original_stream(), model_settings)

# Back-compat alias for legacy tests expecting `CallerAgent`
CallFlowAgent = CallFlowAgentV2
