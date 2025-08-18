"""
Generative Objection Handling System
This module implements a dynamic, LLM-based objection handling engine with strategy tracking.
"""
import logging
import json
import time # Added import for time module
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import yaml
import re
from pivot_controller import pivot_controller

# Import new components
from conversation_state_manager import ConversationStateManager, StrategyTracker, StrategyType
from transition_evaluator import TransitionEvaluator, ConditionType
from context_integrator import ContextIntegrator, IntegrationStyle
from dynamic_strategy_generator import DynamicStrategyGenerator
from state_manager import CallFlowState # Import CallFlowState

@dataclass
class GenerativeObjectionContext:
    """
    Holds all necessary context for generating a dynamic objection response.
    """
    node_id: str
    user_utterance: str
    conversation_history: List[str] = field(default_factory=list)
    persona: str = 'S' # Default to 'S' persona
    node_goal: str = ""
    transition_conditions: Dict[str, str] = field(default_factory=dict)
    used_strategies: List[str] = field(default_factory=list)
    attempt_number: int = 1
    last_user_statement: Optional[str] = None
    requires_goal_achievement: bool = True


class EnhancedPromptBuilder:
    """
    Constructs detailed prompts for the LLM based on conversation context and strategy requirements.
    """
    def __init__(self, config: Dict[str, Any]):
        # Allow passing minimal configs from tests; support optional prompt_template override
        self.config = config or {}
        try:
            tpl = self.config.get("prompt_template")
        except Exception:
            tpl = None
        self.base_template = tpl if tpl else self._get_base_template()
        
    def build(self, context: GenerativeObjectionContext, 
              strategy: Optional[StrategyType] = None,
              integration_hint: Optional[str] = None) -> str:
        """
        Assembles the final prompt from a template and the given context.
        
        Args:
            context: The conversation context
            strategy: Optional specific strategy to use
            integration_hint: Optional hint for context integration
        """
        # Build strategy instruction
        strategy_instruction = self._build_strategy_instruction(strategy, context.used_strategies)
        
        # Build integration instruction
        integration_instruction = self._build_integration_instruction(
            context.last_user_statement, 
            integration_hint
        )
        
        # Build the prompt
        prompt = self.base_template.format(
            node_goal=context.node_goal,
            transition_conditions=json.dumps(context.transition_conditions, indent=2) if isinstance(context.transition_conditions, (dict, list)) else str(context.transition_conditions),
            persona=context.persona,
            conversation_history="\n".join(context.conversation_history[-6:]),  # Last 6 turns
            user_utterance=context.user_utterance,
            strategy_instruction=strategy_instruction,
            integration_instruction=integration_instruction,
            used_strategies=", ".join(context.used_strategies) if context.used_strategies else "None",
            attempt_number=context.attempt_number
        )
        
        return prompt
    
    def _get_base_template(self) -> str:
        """Provides the enhanced prompt template"""
        return """You are an expert AI phone setter having a natural conversation. Your goal is to handle objections smoothly and guide the conversation forward.

**CRITICAL RULES:**
1. Your response must be 2-3 short sentences maximum.
2. Use 6th-grade reading level language.
3. End with a question that aims to achieve the node's goal.
4. NEVER repeat the same strategy or approach that's been used before.
5. Sound natural and conversational, not robotic or scripted.
6. Adapt your tone to the user's personality type (DISC model).

**Context:**
- Current Node Goal: {node_goal}
- Transition Conditions: {transition_conditions}
- User's Personality Type: {persona}
- Attempt Number: {attempt_number}
- Previously Used Strategies: {used_strategies}

**Strategy Instruction:**
{strategy_instruction}

**Integration Instruction:**
{integration_instruction}

**Conversation History (Recent):**
{conversation_history}

**User's Latest Response:**
"{user_utterance}"

**Your Task:**
Generate a response that:
1. Naturally acknowledges or integrates what the user just said (don't ignore them)
2. Handles their objection using the specified strategy
3. Pivots back to achieving the node goal with a different angle than before
4. Ends with a question that guides toward the transition condition

Remember: Each attempt must use a FUNDAMENTALLY DIFFERENT approach, not just different words saying the same thing."""

    def _build_strategy_instruction(self, strategy: Optional[StrategyType], 
                                   used_strategies: List[str]) -> str:
        """Build strategy-specific instructions"""
        if not strategy:
            return "Choose an appropriate strategy that hasn't been used before."
            
        strategy_instructions = {
            StrategyType.DIRECT_VALUE: "Focus on the direct monetary value and benefits. Be straightforward about the $20k monthly potential.",
            StrategyType.IMPACT_FOCUS: "Focus on how this would impact their life, family, and future. Paint a picture of the transformation.",
            StrategyType.SOCIAL_PROOF: "Use examples of others' success. Mention the 7,500+ students achieving results.",
            StrategyType.LOGICAL_REASONING: "Use logic and math. Break down how 10 sites at $2k each = $20k monthly.",
            StrategyType.EMOTIONAL_APPEAL: "Connect emotionally. Share a brief personal insight or feeling about the opportunity.",
            StrategyType.SCARCITY_URGENCY: "Create urgency without being pushy. Mention limited spots or timing advantages.",
            StrategyType.AUTHORITY_CREDIBILITY: "Leverage credibility. Mention your background or the company's track record.",
            StrategyType.PROBLEM_AGITATION: "Highlight the cost of inaction. What are they losing by not exploring this?",
            StrategyType.FUTURE_PACING: "Help them visualize their future with this income. Where will they be in 6 months?",
            StrategyType.REFRAME_PERSPECTIVE: "Completely reframe their objection. Show them a different way to look at it."
        }
        
        instruction = strategy_instructions.get(strategy, "Use a creative approach.")
        
        # Add warning about used strategies
        if used_strategies:
            instruction += f"\n\nDO NOT use these approaches again: {', '.join(used_strategies)}"
            
        return instruction
        
    def _build_integration_instruction(self, last_statement: Optional[str], 
                                      hint: Optional[str]) -> str:
        """Build instructions for context integration"""
        if not last_statement:
            return "Start fresh with your response."
            
        if hint:
            return f"The user just said: '{last_statement}'. {hint}"
            
        # Analyze what kind of integration is needed
        if '?' in last_statement:
            return f"The user asked: '{last_statement}'. Answer briefly, then pivot to your main point."
        elif 'but' in last_statement.lower():
            return f"The user expressed concern: '{last_statement}'. Acknowledge it naturally."
        elif any(word in last_statement.lower() for word in ['company', 'trust', 'legitimate']):
            return f"The user mentioned: '{last_statement}'. Weave in credibility while making your point."
        else:
            return f"The user said: '{last_statement}'. Acknowledge if relevant, but don't dwell on it."


# Back-compat alias for legacy tests
PromptBuilder = EnhancedPromptBuilder

class ResponseValidator:
    """
    Validates the LLM's response against enhanced rules.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.context_integrator = ContextIntegrator()
        
    def validate(self, response: str, context: Optional[GenerativeObjectionContext] = None) -> bool:
        """
        Validates the generated response.
        Context is optional for legacy/isolated validation tests.
        """
        try:
            text = (response or "").strip()
            # Check sentence count (allowing for slight flexibility)
            sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
            if len(sentences) > 4:  # Allow up to 4 short sentences
                logging.warning(f"Response too long: {len(sentences)} sentences")
                return False
                
            # Check if it ends with a question
            if not text.endswith('?'):
                logging.warning("Response doesn't end with a question")
                return False
                
            # Check for repetition of previous responses if context provided
            if context and getattr(context, "conversation_history", None):
                for prev in context.conversation_history[-3:]:  # Check last 3 responses
                    if self._is_too_similar(text, prev):
                        logging.warning("Response too similar to previous")
                        return False
                        
            # Check for robotic patterns
            cleaned = self.context_integrator.avoid_robotic_patterns(text)
            if cleaned != text:
                logging.warning("Response contains robotic patterns")
                return False
                
            # Check for denylisted phrases (support both root and validation.banned_phrases)
            cfg = self.config or {}
            validation_cfg = cfg.get('validation', {}) if isinstance(cfg, dict) else {}
            banned_phrases = (
                cfg.get('denylist')
                or cfg.get('banned_phrases')
                or validation_cfg.get('banned_phrases')
                or [
                    "as an ai", "i am a language model", "i cannot", "i don't have the ability"
                ]
            )
            lower_text = text.lower()
            for phrase in banned_phrases:
                if phrase.lower() in lower_text:
                    logging.warning(f"Response contains banned phrase: {phrase}")
                    return False
                    
            return True
        except Exception as e:
            logging.error(f"ResponseValidator.validate error: {e}", exc_info=True)
            return False
        
    def _is_too_similar(self, response1: str, response2: str) -> bool:
        """Check if two responses are too similar"""
        # Simple similarity check - can be enhanced
        words1 = set(response1.lower().split())
        words2 = set(response2.lower().split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
            
        overlap = len(words1.intersection(words2))
        similarity = overlap / max(len(words1), len(words2))
        
        return similarity > 0.7  # 70% similarity threshold


class ResponseOrchestrator:
    """
    Orchestrates all components to generate appropriate responses.
    """
    def __init__(self, call_flow_state: CallFlowState, conversation_state_manager: ConversationStateManager, kb_processor: Optional[Any] = None):
        self.call_flow_state = call_flow_state
        self.conversation_state_manager = conversation_state_manager
        self.strategy_tracker = StrategyTracker(conversation_state_manager)
        self.transition_evaluator = TransitionEvaluator(self.call_flow_state)
        self.context_integrator = ContextIntegrator()
        self.strategy_generator = DynamicStrategyGenerator()
        self.prompt_builder = EnhancedPromptBuilder(_load_config())
        self.validator = ResponseValidator(_load_config())
        self.kb_processor = kb_processor
        self.last_orchestrator_result: Optional[Dict[str, Any]] = None # New attribute
        
    def generate_response(self, user_input: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete response handling objections and managing flow.
        
        Returns:
            Dict containing:
            - response: The generated response
            - should_transition: Whether to move to next node
            - target_node: Which node to transition to
            - retry_goal: Whether to retry the current node's goal
            - identified_objection: The identified objection type
            - selected_strategy: The strategy chosen to address the objection
        """
        # Extract node information
        node_id = node_data.get('id', '')
        node_goal = node_data.get('goal', '')
        transition_conditions = self.transition_evaluator.extract_transition_conditions_from_node(node_data)
        
        logging.debug(f"Orchestrator.generate_response: Node ID: {node_id}, Goal: {node_goal}, Transition Conditions: {transition_conditions}")

        # FIRST: Check for an explicit objection transition defined on the node
        identified_objection_early = self._identify_objection(user_input, node_id)
        transitions_list = node_data.get('transitions', []) or []
        objection_target_node = None
        for t in transitions_list:
            if t.get('condition') == identified_objection_early:
                objection_target_node = t.get('target')
                break

        if objection_target_node is not None:
             logging.info(f"Orchestrator: Early objection transition found. Routing '{identified_objection_early}' to '{objection_target_node}'.")
             # We still need to generate a compliant response before transitioning.
             response, _, _ = self._generate_objection_response(user_input, node_data, should_retry=False, objection=identified_objection_early)
             if response:
                 response = self._finalize_compliant_response(response, node_data, user_input)
                 pivot_controller.register_bot_utterance(response, node_id)
             result = {
                 'response': response,
                 'should_transition': True,
                 'target_node': objection_target_node,
                 'retry_goal': False,
                 'identified_objection': identified_objection_early,
                 'selected_strategy': None,
             }
             self.last_orchestrator_result = result
             return result

        # Check if transition condition is met
        condition_met, target_node, condition_desc = self.transition_evaluator.evaluate_response(
            user_input, transition_conditions
        )
        
        # Determine if we need to retry the goal
        should_retry = self.transition_evaluator.should_retry_node_goal(
            user_input,
            transition_conditions,
            self.state_manager.current_node_state.attempts if self.state_manager.current_node_state else 0
        )
        logging.info(f"Orchestrator.generate_response: user_input='{user_input}', condition_met={condition_met}, target_node={target_node}, should_retry={should_retry}")
        
        # PivotController integration: if we detected an affirmative but there is no explicit
        # affirmative path on this node, and the last bot turn ended with a question (pivot),
        # then advance via the default transition (if available) instead of retrying.
        if condition_desc == "affirmative_after_pivot_default":
            logging.info("Advancing via default transition due to affirmative response after pivot.")
            # Ensure a response is provided even if the orchestrator didn't generate one
            # This is crucial for acknowledging the user's affirmative and preventing silence
            response_text = "" # Default bridging response
            
            result = {
                'response': response_text,
                'should_transition': True,
                'target_node': target_node,
                'retry_goal': False,
                'identified_objection': 'affirmative_pivot',
                'selected_strategy': None,
            }
            self.last_orchestrator_result = result
            return result
        
        # If a transition condition is met, we generally shouldn't retry the goal,
        # with the exception of questions, where answering them is part of the goal.
        if condition_met and not should_retry:
            final_should_transition = True
            final_target_node = target_node
            final_retry_goal = False

        # Use the early-identified objection throughout to avoid duplicate calls
        identified_objection = identified_objection_early
        is_info_seeking_question = identified_objection in {"business_model_question", "pricing_question", "information_question"}
        logging.debug(f"Orchestrator.generate_response: Identified objection: {identified_objection}, Is info-seeking question: {is_info_seeking_question}")

        # Determine target node based on identified objection, if a specific transition is defined
        transitions_list = node_data.get('transitions', []) or []
        lookup_key = identified_objection
        # Back-compat mapping for environments using 'objection_or_callback_request'
        if identified_objection == "callback_request":
            lookup_key = "objection_or_callback_request"
        
        objection_target_node = None
        for t in transitions_list:
            if t.get('condition') == lookup_key:
                objection_target_node = t.get('target')
                break
        
        if objection_target_node:
            logging.info(f"Orchestrator: Early objection transition found. Routing '{identified_objection}' to '{objection_target_node}'.")
            # Check for silent transition based on the identified objection
            if identified_objection in EARLY_SILENT_TRANSITIONS:
                logging.info(f"Performing silent transition for objection: {identified_objection}")
                return self._format_response(
                    response="",
                    should_transition=True,
                    target_node=objection_target_node,
                    identified_objection=identified_objection,
                    selected_strategy=StrategyType.SILENT_TRANSITION
                )

            # Generate a response for the objection, but ensure we transition
            response, _, _ = self._generate_objection_response(user_input, node_data, True, objection=identified_objection) # Force should_retry=True to ensure WEAVE style
            if response:
                response = self._finalize_compliant_response(response, node_data, user_input)
                pivot_controller.register_bot_utterance(response, node_id)
            result = {
                'response': response,
                'should_transition': True,
                'target_node': objection_target_node,
                'retry_goal': False, # No retry needed as we are transitioning
                'identified_objection': identified_objection,
                'selected_strategy': None # Strategy is handled by _generate_objection_response
            }
            self.last_orchestrator_result = result
            logging.info(f"Orchestrator.generate_response: Returning objection-based transition: {result}")
            return result

        # Generate a proper objection response for questions and objections
        logging.debug(f"Orchestrator.generate_response: Generating objection response for user input: '{user_input}'")
        if node_id in ("N001A_NameConfirmation_Only", "N001B_IntroAndHelpRequest_Only") and condition_met:
            # For these early nodes, when the default transition condition is met,
            # do not generate or speak an objection response; transition silently.
            response, selected_strategy = "", None
        else:
            response, identified_objection, selected_strategy = self._generate_objection_response(
                user_input, node_data, should_retry, objection=identified_objection
            )
        
        # Determine final transition based on identified objection and node data
        final_should_transition = False
        final_target_node = None
        final_retry_goal = should_retry # Default to should_retry from transition_evaluator

        # Prioritize specific objection-based transitions
        transitions_list = node_data.get('transitions', []) or []
        final_lookup_key = identified_objection
        if identified_objection == "callback_request":
            final_lookup_key = "objection_or_callback_request"
        objection_target_node = None
        for t in transitions_list:
            if t.get('condition') == final_lookup_key:
                objection_target_node = t.get('target')
                break
        if objection_target_node:
            final_should_transition = True
            final_target_node = objection_target_node
            final_retry_goal = False # No retry needed if transitioning

        # Special handling for N001A_NameConfirmation_Only to transition immediately if condition met
        elif node_id in ("N001A_NameConfirmation_Only", "N001B_IntroAndHelpRequest_Only") and condition_met:
            final_should_transition = True
            final_target_node = target_node
            final_retry_goal = False

        # For information-seeking questions: if a transition target was identified (e.g., via default),
        # transition after answering; otherwise retry the goal.
        elif identified_objection in {"business_model_question", "pricing_question", "information_question", "company_question"}:
            if condition_met:
                final_should_transition = True
                final_target_node = target_node
                final_retry_goal = False
            else:
                final_should_transition = False
                final_target_node = None
                final_retry_goal = True  # Retry goal when we don't have a clear transition target

        # If condition met and no retry needed, and no specific objection transition, then transition
        elif condition_met and not should_retry:
            final_should_transition = True
            final_target_node = target_node
            final_retry_goal = False

        # Finalize and register only if we actually have a response to speak
        if response:
            response = self._finalize_compliant_response(response, node_data, user_input)
            pivot_controller.register_bot_utterance(response, node_id)

        result = {
            'response': response,
            'should_transition': final_should_transition,
            'target_node': final_target_node,
            'retry_goal': final_retry_goal,
            'identified_objection': identified_objection,
            'selected_strategy': selected_strategy.value if isinstance(selected_strategy, StrategyType) else selected_strategy
        }
        self.last_orchestrator_result = result
        logging.info(f"Orchestrator.generate_response: Final response being returned: {result}")
        return result
        
    def _generate_objection_response(self, user_input: str,
                                    node_data: Dict[str, Any],
                                    should_retry: bool,
                                    objection: Optional[str] = None) -> (str, str, Optional[StrategyType]):
        """Generate response handling objection"""
        # Identify the objection type if not provided
        if objection is None:
            objection = self._identify_objection(user_input, node_data.get('id'))
        logging.info(f"Orchestrator._generate_objection_response: user_input='{user_input}', identified_objection='{objection}', should_retry={should_retry}")
        
        # Get next strategy
        strategy = self.strategy_tracker.get_next_strategy(
            objection,
            self.strategy_generator.get_strategy_sequence(objection)
        )
        logging.debug(f"Orchestrator._generate_objection_response: Selected strategy: {strategy.value if strategy else 'None'}")
        
        if not strategy:
            # All strategies exhausted
            logging.warning("All strategies exhausted, using fallback")
            return "I understand. Let me know if you change your mind.", objection, None
            
        # Build context
        context = GenerativeObjectionContext(
            node_id=node_data.get('id', ''),
            user_utterance=user_input,
            conversation_history=self.state_manager.get_recent_history(include_interrupted=False), # Exclude interrupted turns
            persona=self.state_manager.personality_type,
            node_goal=node_data.get('goal', ''),
            transition_conditions=self.transition_evaluator.extract_transition_conditions_from_node(node_data),
            used_strategies=[s for s in self.state_manager.global_strategies_used.get(objection, [])],
            attempt_number=self.state_manager.current_node_state.attempts + 1 if self.state_manager.current_node_state else 1,
            last_user_statement=self.state_manager.get_last_user_utterance(),
            requires_goal_achievement=should_retry
        )
        logging.debug(f"Orchestrator._generate_objection_response: Context built: {context}")
        
        # Generate response using strategy
        start_generate_with_strategy = time.perf_counter()
        generated_response = self._generate_with_strategy(context, strategy, objection)
        end_generate_with_strategy = time.perf_counter()
        logging.debug(f"TIMING: _generate_with_strategy took {end_generate_with_strategy - start_generate_with_strategy:.4f} seconds")

        # If the generated response is already compliant, respect it as-is.
        try:
            if self.validator.validate(generated_response, context):
                logging.info("Orchestrator._generate_objection_response: Using generated response as-is (already compliant).")
                return generated_response, objection, strategy
        except Exception as _e:
            logging.debug(f"Orchestrator._generate_objection_response: Validator pre-check failed, proceeding to integration: {_e}")
        
        # Integrate context if needed
        # Policy: ensure explicit acknowledgment for non-information objections.
        info_types = {"business_model_question", "pricing_question", "information_question", "company_question", "question"}
        integration_style = IntegrationStyle.WEAVE if objection in info_types else IntegrationStyle.ACKNOWLEDGE
        logging.info(f"Orchestrator._generate_objection_response: Integrating context with style={integration_style.value}")
        logging.debug(f"Orchestrator._generate_objection_response: generated_response BEFORE integration: '{generated_response}'")
        final_response_from_integrator_step = self.context_integrator.integrate_user_context(
            user_input,
            generated_response,
            integration_style
        )
        logging.debug(f"Orchestrator._generate_objection_response: generated_response AFTER integration: '{final_response_from_integrator_step}'")
        logging.info(f"Orchestrator: objection='{objection}', strategy='{strategy.value if strategy else None}', should_retry={should_retry}")
        logging.debug(f"Orchestrator._generate_objection_response: Response before returning: '{final_response_from_integrator_step}'")
            
        return final_response_from_integrator_step, objection, strategy
        
    def _generate_with_strategy(self, context: GenerativeObjectionContext,
                                strategy: StrategyType, objection: str) -> str:
        """Generate response using specific strategy"""
        logging.debug(f"Orchestrator._generate_with_strategy: Generating response with strategy: {strategy.value}, objection: {objection}")
        # Generate core strategic content from the strategy generator
        template_response = self.strategy_generator.generate_strategy_response(
            objection,
            strategy,
            {'income_amount': '$20k'}
        )
        logging.debug(f"Orchestrator._generate_with_strategy: Template response: '{template_response}'")

        # Information-seeking path: prefer concise KB-backed answer, then pivot
        info_types = {"business_model_question", "pricing_question", "information_question", "company_question"}
        if objection in info_types:
            answer = ""
            try:
                if self.kb_processor:
                    start_kb_query = time.perf_counter()
                    kb_result = self.kb_processor.query(context.user_utterance)
                    end_kb_query = time.perf_counter()
                    logging.debug(f"TIMING: KBProcessor.query took {end_kb_query - start_kb_query:.4f} seconds")
                    logging.debug(f"Orchestrator._generate_with_strategy: KB query result type={type(kb_result).__name__}, preview='{str(kb_result)[:160]}'")
                    if isinstance(kb_result, dict):
                        kb_answer = (kb_result.get("answer") or kb_result.get("response") or "").strip()
                    else:
                        kb_answer = str(kb_result or "").strip()
                    logging.info(f"Orchestrator._generate_with_strategy: KB raw answer='{kb_answer}'")
                    answer = kb_answer
                    logging.info("Orchestrator._generate_with_strategy: KB answer used as-is.")
            except Exception as e:
                logging.warning(f"KB query failed, falling back to templates: {e}")

            if not answer:
                logging.debug("Orchestrator._generate_with_strategy: KB answer not found, using fallback templates.")
                # Fallback templates if KB is unavailable
                if objection == "business_model_question":
                    answer = "We build simple sites that rank on Google for local services and sell the inbound leads to businesses."
                elif objection == "pricing_question":
                    answer = "Most people start between five and fifteen thousand depending on goals and scope."
                else:
                    answer = "We handle the technical work while you focus on simple steps that move you forward."

            # Clamp KB answers to two sentences and ensure proper punctuation
            original_sentences = [s.strip() for s in re.split(r'[.!?]+', answer) if s.strip()]
            clamped_sentences = original_sentences[:2] # Keep at most two sentences
            
            # Ensure proper punctuation for clamped sentences
            clamped_answer = ""
            if clamped_sentences:
                clamped_answer = ". ".join(clamped_sentences)
                if not clamped_answer.endswith(('.', '!', '?')):
                    clamped_answer += "." # Ensure it ends with a period if no other punctuation

            # Add structured logs for clamping
            if len(original_sentences) > len(clamped_sentences):
                logging.info(f"TELEMETRY: {{ event: kb_clamped, sentences_kept: {len(clamped_sentences)}, original_sentences: {len(original_sentences)} }}")
            
            # Persona/light enhancement
            if context.persona == 'I':
                clamped_answer = clamped_answer.replace(".", "!")

            # Append a safe pivot question (prefer per-node pivot from config)
            pivot_q = " Does that make sense so far?"
            try:
                cfg = _load_config()
                pivot_map = (cfg.get("pivot_map", {}) or {})
                mapped = pivot_map.get(context.node_id)
                if isinstance(mapped, str) and mapped.strip():
                    pivot_q = f" {mapped.strip()}"
            except Exception:
                pass

            composed = f"{clamped_answer.rstrip()} {pivot_q}".strip()
            logging.info(f"Orchestrator._generate_with_strategy: Composed KB+Pivot response: '{composed}'")
            # Do NOT register here; orchestrator will register finalized text
            return composed

        # Non-info path: enhance the template and validate
        prompt = self.prompt_builder.build(context, strategy)
        logging.debug(f"Orchestrator._generate_with_strategy: Prompt for LLM enhancement: '{prompt}'")

        enhanced_response = self._enhance_response(template_response, context)
        logging.info(f"Orchestrator._generate_with_strategy: Final enhanced_response='{enhanced_response}'")

        # Validate response; fallback to template if invalid
        if not self.validator.validate(enhanced_response, context):
            logging.warning("Orchestrator._generate_with_strategy: Enhanced response failed validation, falling back to template response.")
            return template_response

        # Do NOT register here; orchestrator will register finalized text
        return enhanced_response
        
    def _enhance_response(self, template_response: str, context: GenerativeObjectionContext) -> str:
        """
        Enhance template response (placeholder for actual LLM call)
        In production, this would make an actual LLM API call
        """
        # This is where you would call OpenAI/Anthropic/etc API
        # For now, return a slightly modified version
        
        # Add personality-based adjustment
        if context.persona == 'D':
            # Direct and results-focused
            template_response = template_response.replace("Would you", "Will you")
        elif context.persona == 'I':
            # Enthusiastic and social
            template_response = template_response.replace(".", "!")
        elif context.persona == 'S':
            # Supportive and steady — avoid pronoun substitutions to prevent grammar issues
            # Keep the original wording to maintain grammatical correctness.
            pass
        elif context.persona == 'C':
            # Detailed and logical
            template_response = template_response.replace("about", "specifically")
            
        return template_response

    def _finalize_compliant_response(self, text: str, node_data: Dict[str, Any], user_input: str) -> str:
        """
        Last-mile sanitation to ensure the response:
        - Avoids robotic patterns
        - Is concise (<= 3 short sentences)
        - Ends with a question
        - Avoids banned phrases
        """
        try:
            t = (text or "").strip()
            # Remove robotic patterns
            t = self.context_integrator.avoid_robotic_patterns(t)

            # Replace unresolved template placeholders
            try:
                t = t.replace("{income_amount}", "$20k")
                t = re.sub(r"\{[^}]+\}", "", t)
            except Exception:
                pass

            # Trim excessive sentences
            sentences = [s.strip() for s in re.split(r"[.!?]+", t) if s.strip()]
            if len(sentences) > 3:
                sentences = sentences[:2]  # keep it tight; we'll add one question
                t = ". ".join(sentences).strip()

            # Persona-based softening for S tone
            try:
                persona = getattr(self.state_manager, "personality_type", "S")
            except Exception:
                persona = "S"
            if str(persona).upper() == "S":
                # Avoid auto-prepending stock acknowledgments (e.g., "No rush,")
                # to reduce repetitive tics and keep responses varied.
                pass

            # Ensure ends with a question
            if not t.endswith("?"):
                # Default fallback question, but prefer per-node pivot from config if available
                fallback_q = "Does that make sense so far?"
                node_id = node_data.get("id", "") if isinstance(node_data, dict) else ""
                try:
                    cfg = _load_config()
                    pivot_map = (cfg.get("pivot_map", {}) or {})
                    mapped = pivot_map.get(node_id)
                    if isinstance(mapped, str) and mapped.strip():
                        fallback_q = mapped.strip()
                except Exception:
                    pass
                t = f"{t.rstrip('. ')} {fallback_q}".strip()

            # Remove banned phrases and meta-language
            banned = _load_config().get('banned_phrases', []) + ["feel free to ask for more details!"]
            # Replace each banned phrase insensitively
            for phrase in banned:
                if not phrase:
                    continue
                t = re.sub(re.escape(phrase), "", t, flags=re.IGNORECASE)
                t = re.sub(r"\s{2,}", " ", t).strip()

            return t
        except Exception as e:
            logging.warning(f"_finalize_compliant_response failed: {e}")
            # Best effort: ensure ending question
            t = (text or "").strip()
            if not t.endswith("?"):
                t = f"{t} Does that make sense so far?"
            return t
        
    def _identify_objection(self, user_input: str, node_id: Optional[str] = None) -> str:
        """Identify the type of objection"""
        user_lower = user_input.lower()
        
        # Prioritize specific, non-information-seeking objections
        # Callback request should be prioritized over no_time if both are present
        if any(word in user_lower for word in ['call me back', 'ring me later', 'another time', 'call back later', 'call back']):
            return "callback_request"
        elif any(word in user_lower for word in ['busy', 'time', 'meeting', 'have to go', 'gotta run']):
            return "no_time"
        elif any(word in user_lower for word in ['not interested', "don't want", "this isn't for me"]):
            return "not_interested"
        # Make 'no_recall' more specific to avoid capturing general questions
        elif any(phrase in user_lower for phrase in ['i don\'t recall', 'don\'t remember', 'doesn\'t ring a bell', 'who are you again']):
            return "no_recall"
        elif any(word in user_lower for word in ['scam', 'trust', 'legitimate']):
            return "skeptical"
        elif any(word in user_lower for word in ['money', 'afford', 'broke']):
            return "no money"
        elif any(word in user_lower for word in ['think', 'consider', 'maybe']):
            return "need to think"
        
        # Then check for information-seeking questions, with special handling for N001B
        is_question = '?' in user_input
        is_information_seeking = any(phrase in user_lower for phrase in ['what', 'how', 'explain', 'tell me', "don't know", "not sure", "know about"])

        if is_question or is_information_seeking:
            if any(word in user_lower for word in ['business', 'model', 'work', 'it does']):
                return "business_model_question"
            elif any(word in user_lower for word in ['cost', 'price', 'much', 'pay']):
                return "pricing_question"
            # Explicitly check for company questions, but not for N001B_IntroAndHelpRequest_Only
            elif node_id != "N001B_IntroAndHelpRequest_Only" and ('who are you' in user_lower or 'your company' in user_lower or 'what company' in user_lower):
                return "company_question"
            elif any(phrase in user_lower for phrase in ['what is this', 'tell me more', 'what are you calling about']):
                return "question" # General question that is not specific to business, pricing, or company
            else:
                return "information_question" # Catch-all for other info-seeking questions
        else:
            return "general" # Default for non-objection, non-question inputs
            
    def _has_additional_context(self, user_input: str) -> bool:
        """Check if user added context beyond simple agreement"""
        simple_agreements = ['yes', 'yeah', 'yep', 'sure', 'okay', 'ok', 'yup']
        user_lower = user_input.lower().strip()
        
        # If it's just a simple agreement, no additional context
        if user_lower in simple_agreements:
            return False
            
        # If it contains "but" or questions, there's additional context
        if 'but' in user_lower or '?' in user_input:
            return True
            
        # If it's longer than 3 words, probably has context
        if len(user_input.split()) > 3:
            return True
            
        return False
        
    def _generate_transition_acknowledgment(self, user_input: str, target_node: str) -> str:
        """Generate brief acknowledgment before transitioning"""
        # This would integrate their concern into the transition
        acknowledgments = [
            "I hear you on that.",
            "That's a fair point.",
            "Good to know.",
            "I appreciate you sharing that.",
            "That makes sense."
        ]
        
        import random
        acknowledgment = random.choice(acknowledgments)
        logging.info(f"Orchestrator._generate_transition_acknowledgment: Returning acknowledgment='{acknowledgment}' for user_input='{user_input}'")
        return acknowledgment


def _load_config() -> Dict[str, Any]:
    """Loads configuration from the YAML file."""
    try:
        with open('generative_handler_config.yml', 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.info("Config file not found, using defaults")
        return {
            'banned_phrases': [
                "as an ai", "i am a language model", "i cannot",
                "i don't have the ability", "my programming"
            ],
            'max_response_length': 100,
            'max_attempts': 3,
            'early_silent_transitions': [
                'affirmative_name_confirmation', 'affirmative_intro_and_help_request',
                'objection_opener_company_question', 'wrong_number', 'not_interested_early'
            ]
        }
    except yaml.YAMLError as e:
        logging.error(f"Error parsing config: {e}")
        return {}

EARLY_SILENT_TRANSITIONS = _load_config().get('early_silent_transitions', [])


def generate_objection_response(context: GenerativeObjectionContext) -> str:
    """
    The main function to generate a dynamic objection response.
    This is the legacy interface maintained for compatibility.
    """
    # Create a minimal state manager for standalone use
    state_manager = ConversationStateManager()
    
    # Add conversation history
    for turn_str in context.conversation_history:
        if turn_str.startswith("USER:"):
            state_manager.add_turn("user", turn_str[5:].strip())
        elif turn_str.startswith("AGENT:"):
            # Assuming for legacy compatibility, agent turns are not interrupted here
            state_manager.add_turn("agent", turn_str[6:].strip())
            
    # Set personality
    state_manager.set_personality_type(context.persona)
    
    # Create orchestrator
    orchestrator = ResponseOrchestrator(state_manager)
    
    # Create node data from context
    node_data = {
        'id': context.node_id,
        'goal': context.node_goal,
        'transition_conditions': context.transition_conditions
    }
    
    # Generate response
    result = orchestrator.generate_response(context.user_utterance, node_data)
    
    return result.get('response', "I understand. Let me know if you'd like to explore this further.")


# For testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Test with actual conversation scenario
    state_manager = ConversationStateManager()
    orchestrator = ResponseOrchestrator(state_manager)
    
    # Simulate conversation
    node_data = {
        'id': 'N_Opener',
        'goal': 'Get user to express interest in $20k monthly income',
        'transition_conditions': {
            'interest': 'N_NextNode',
            'objection': 'N_ObjectionHandler',
            'default': 'N_Default'
        }
    }
    
    # First objection
    print("\n=== First 'busy' objection ===")
    result1 = orchestrator.generate_response("I'm busy", node_data)
    print(f"Response: {result1['response']}")
    
    # Second same objection
    print("\n=== Second 'busy' objection ===")
    result2 = orchestrator.generate_response("Still busy", node_data)
    print(f"Response: {result2['response']}")
    
    # Third same objection
    print("\n=== Third 'busy' objection ===")
    result3 = orchestrator.generate_response("I told you I'm busy", node_data)
    print(f"Response: {result3['response']}")
