"""
Objection Handling System
Implements the "Indomitable Closer" Multi-Phase Objection Handling Engine
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import re
import json
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field

# Import GDP phrase banks and node goals
from gdp_phrases import GDP_PHRASE_BANKS, NODE_GOALS_AND_CRITERIA

# Dynamic framework (minimal slice) — optional import
try:
    from dynamic_objection_framework import DynamicHandlerRegistry, build_minimal_registry
except Exception:
    DynamicHandlerRegistry = None
    build_minimal_registry = None

# ===== A1 scaffolding: module-level logger =====
logger = logging.getLogger(__name__)

# ===== A2 flags (global + AB guard + node×persona) — defaults OFF to preserve legacy =====
# A1 flags retained; A2 introduces consolidated FLAGS and guard helpers
FLAGS: Dict[str, object] = {
    'engine_global': True,  # must be True to activate the new engine at all
    'ab_guard': {'enabled': True, 'percent': 0},  # stable cohort via thread_id; 0% by default
    'kb_splice': False,  # A3 optional splice OFF by default
    'bridge_pivot_enforcement': True,  # Enforce contextual bridge + pivot composition
    'dynamic_opener_s_enabled': True, # New flag for dynamic opener S path
    'nodes': {
        'IntroduceModel': {'D': False, 'I': False, 'S': True, 'C': False},
        'KB_QA': {'D': False, 'I': False, 'S': True, 'C': False},
        'IncomeBackground': {'D': False, 'I': False, 'S': False, 'C': False},
        'FinancialQualification': {'D': False, 'I': False, 'S': False, 'C': False},
        'Commitment': {'D': False, 'I': False, 'S': False, 'C': False},
        'Scheduling': {'D': False, 'I': False, 'S': False, 'C': False},
    },
}
# Keep A1 feature_flags map for backward compatibility toggles used elsewhere
feature_flags: Dict[str, Dict[str, bool]] = {
    'D': {'IntroduceModel': False},
    'I': {'IntroduceModel': False},
    'S': {'IntroduceModel': False},
    'C': {'IntroduceModel': False},
}

# Persona response banks for IntroduceModel only for A1; minimal, neutral placeholders
# Keyed by persona ('D','I','S','C') -> node_id -> objection_type -> list[str]
response_banks: Dict[str, Dict[str, Dict[str, List[str]]]] = {
    'D': {
        'IntroduceModel': {
            # In A1 we keep a single simple type "general" to exercise rotation
            'general': [
                "Here's the core idea in plain terms.",
                "Let me give you the quick version.",
            ]
        }
    },
    'I': {},
    'S': {},
    'C': {},
}

# ===== A2: Context object and MVP registry =====
@dataclass
class ObjectionContext:
    """Normalized propagation context. occurrence is maintained per (thread_id,node_id,objection_cat)."""
    thread_id: str
    node_id: str
    objection_category: str
    objection_type: str
    persona: str
    # A2: track occurrences for a given (thread_id, node_id, objection_category)
    occurrence: int = field(default_factory=lambda: defaultdict(int))
    # A2: track last used response for a given (thread_id, node_id, objection_category)
    last_response_hash: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.occurrence, defaultdict):
            self.occurrence = defaultdict(int, self.occurrence)

    def increment_occurrence(self):
        key = (self.thread_id, self.node_id, self.objection_category)
        self.occurrence[key] += 1
        logger.debug(f"Incremented occurrence for {key}: {self.occurrence[key]}")

    def get_occurrence(self) -> int:
        key = (self.thread_id, self.node_id, self.objection_category)
        return self.occurrence[key]

    def set_last_response_hash(self, response_hash: str):
        self.last_response_hash = response_hash

    def get_last_response_hash(self) -> Optional[str]:
        return self.last_response_hash

@dataclass
class ObjectionResponse:
    """Standardized response from the objection handler."""
    response: str
    response_type: str  # e.g., "canned", "dynamic", "gdp"
    context_updated: bool = False
    # A2: Add a hash of the response for tracking last used response
    response_hash: Optional[str] = None

# A2: Minimal dynamic handler registry for MVP
dynamic_registry: Optional[DynamicHandlerRegistry] = None
if DynamicHandlerRegistry:
    dynamic_registry = build_minimal_registry()

# ===== A2: AB guard helper =====
def _is_ab_test_enabled(thread_id: str) -> bool:
    """
    Determines if the AB test is enabled for a given thread_id based on FLAGS.
    A simple hash-based bucketing ensures a stable cohort.
    """
    if not FLAGS['ab_guard']['enabled']:
        return False
    
    percent = FLAGS['ab_guard']['percent']
    if percent == 0:
        return False

    # Use a stable hash for bucketing
    hash_object = hashlib.sha256(thread_id.encode())
    hash_digest = int(hash_object.hexdigest(), 16)
    
    # Check if the hash falls within the allocated percentage
    return (hash_digest % 100) < percent

# ===== A2: Node-persona guard helper =====
def _is_node_persona_enabled(node_id: str, persona: str, flag_name: str) -> bool:
    """
    Checks if a specific flag (e.g., 'dynamic_opener_s_enabled') is enabled for a given
    node_id and persona within the FLAGS structure.
    """
    node_flags = FLAGS.get('nodes', {}).get(node_id, {})
    return node_flags.get(persona, False) and FLAGS.get(flag_name, False)

# ===== A1: Core Objection Handling Logic (retained) =====
class ObjectionHandler:
    def __init__(self, persona: str):
        self.persona = persona
        # A2: Use a more robust, thread-safe (if needed) context store
        self.contexts: Dict[str, ObjectionContext] = {} # Keyed by (thread_id, node_id, objection_category)

    def _get_context(self, thread_id: str, node_id: str, objection_category: str, objection_type: str) -> ObjectionContext:
        key = (thread_id, node_id, objection_category)
        if key not in self.contexts:
            self.contexts[key] = ObjectionContext(
                thread_id=thread_id,
                node_id=node_id,
                objection_category=objection_category,
                objection_type=objection_type,
                persona=self.persona
            )
        return self.contexts[key]

    def _select_response(self, context: ObjectionContext, responses: List[str]) -> str:
        """
        Selects a response based on occurrence and last_response_hash.
        Implements a rotation that avoids immediate repetition.
        """
        if not responses:
            return ""

        available_responses = list(responses)
        
        # Filter out the last used response if there are other options
        if context.get_last_response_hash() and len(available_responses) > 1:
            available_responses = [
                r for r in available_responses 
                if hashlib.sha256(r.encode()).hexdigest() != context.get_last_response_hash()
            ]
        
        # If filtering leaves no options, or only the last one, use original list
        if not available_responses:
            available_responses = list(responses)

        # Simple rotation based on current occurrence
        occurrence_in_cycle = context.get_occurrence() % len(available_responses)
        selected_response = available_responses[occurrence_in_cycle]
        
        # Update last_response_hash in context
        context.set_last_response_hash(hashlib.sha256(selected_response.encode()).hexdigest())
        
        return selected_response

    def _build_canned_response(self, context: ObjectionContext) -> ObjectionResponse:
        """
        Constructs a canned response based on persona, node, and objection type.
        A1: Simple rotation based on occurrence.
        """
        bank = response_banks.get(self.persona, {}).get(context.node_id, {}).get(context.objection_type, [])
        response_text = self._select_response(context, bank)
        return ObjectionResponse(response=response_text, response_type="canned", context_updated=True)

    def _build_dynamic_response(self, context: ObjectionContext, user_utterance: str) -> ObjectionResponse:
        """
        Constructs a dynamic response using the dynamic_registry.
        """
        if not dynamic_registry:
            logger.warning("DynamicHandlerRegistry not initialized. Cannot build dynamic response.")
            return ObjectionResponse(response="", response_type="dynamic", context_updated=False)

        try:
            # The dynamic handler will use its own internal logic for selection/rotation
            dynamic_response_text = dynamic_registry.handle_objection(
                persona=context.persona,
                node_id=context.node_id,
                objection_category=context.objection_category,
                objection_type=context.objection_type,
                user_utterance=user_utterance,
                occurrence=context.get_occurrence() # Pass current occurrence for dynamic logic
            )
            if dynamic_response_text:
                return ObjectionResponse(response=dynamic_response_text, response_type="dynamic", context_updated=True)
        except Exception as e:
            logger.error(f"Error building dynamic response: {e}")
        
        return ObjectionResponse(response="", response_type="dynamic", context_updated=False)

    def _build_gdp_response(self, context: ObjectionContext, user_utterance: str) -> ObjectionResponse:
        """
        Constructs a Goal-Directed Pivot (GDP) response.
        This function orchestrates the GDP framework, selecting appropriate phrases
        and ensuring compliance with node goals and criteria.
        """
        logger.info(f"Building GDP response for context: {context}")

        # 1. Determine the current node's goal and criteria
        node_goal_data = NODE_GOALS_AND_CRITERIA.get(context.node_id)
        if not node_goal_data:
            logger.warning(f"No GDP goal data found for node: {context.node_id}. Falling back to canned.")
            return self._build_canned_response(context)

        node_goal = node_goal_data.get("goal", "Advance the conversation.")
        node_criteria = node_goal_data.get("criteria", [])

        # 2. Select a bridge phrase
        bridge_phrases = GDP_PHRASE_BANKS.get(context.persona, {}).get("bridge", [])
        selected_bridge = self._select_response(context, bridge_phrases)
        if not selected_bridge:
            logger.warning("No bridge phrases available. Falling back to canned.")
            return self._build_canned_response(context)

        # 3. Select a pivot phrase
        pivot_phrases = GDP_PHRASE_BANKS.get(context.persona, {}).get("pivot", [])
        selected_pivot = self._select_response(context, pivot_phrases)
        if not selected_pivot:
            logger.warning("No pivot phrases available. Falling back to canned.")
            return self._build_canned_response(context)

        # 4. Compose the GDP response
        gdp_response_text = f"{selected_bridge} {selected_pivot}"
        
        # 5. (Optional) Enforce contextual bridge + pivot composition
        if FLAGS.get('bridge_pivot_enforcement', False):
            # This is a placeholder for more sophisticated logic.
            # In a real system, this might involve:
            # - Checking semantic compatibility between bridge and pivot
            # - Ensuring the combined phrase aligns with node_goal
            # - Using an LLM call to refine the composition
            logger.debug("Bridge + Pivot enforcement enabled (placeholder logic).")

        return ObjectionResponse(response=gdp_response_text, response_type="gdp", context_updated=True)

    def handle_objection(self, thread_id: str, node_id: str, objection_category: str, objection_type: str, user_utterance: str) -> ObjectionResponse:
        """
        Main entry point for objection handling.
        A2: Incorporates AB testing and dynamic handler routing.
        A3: Adds KB splice and dynamic opener S path.
        """
        context = self._get_context(thread_id, node_id, objection_category, objection_type)
        context.increment_occurrence()
        
        logger.info(f"Handling objection: {objection_category}/{objection_type} for node {node_id} (occurrence: {context.get_occurrence()})")

        # A2: Check AB guard
        if _is_ab_test_enabled(thread_id):
            logger.info(f"AB test enabled for thread {thread_id}. Routing to dynamic handler.")
            return self._finalize_return(self._build_dynamic_response(context, user_utterance), context)

        # A3: Dynamic Opener S path
        if _is_node_persona_enabled(node_id, self.persona, 'dynamic_opener_s_enabled') and dynamic_registry:
            logger.info(f"Dynamic Opener S path enabled for node {node_id}, persona {self.persona}. Routing to GDP.")
            return self._finalize_return(self._build_gdp_response(context, user_utterance), context)

        # A3: KB Splice (placeholder for future integration)
        if FLAGS.get('kb_splice', False):
            logger.info("KB splice enabled (placeholder).")
            # In a real scenario, this would involve:
            # 1. Querying KB with user_utterance and context
            # 2. Synthesizing a response from KB results
            # For now, it falls through to dynamic/canned
            pass

        # Fallback to dynamic or canned based on availability and flags
        if dynamic_registry and FLAGS['engine_global']: # Ensure dynamic engine is globally active
            logger.info("Falling back to dynamic handler.")
            return self._finalize_return(self._build_dynamic_response(context, user_utterance), context)
        
        logger.info("Falling back to canned response.")
        return self._finalize_return(self._build_canned_response(context), context)

    def _finalize_return(self, response: ObjectionResponse, context: ObjectionContext) -> ObjectionResponse:
        """
        Ensures the response is compliant and updates context if necessary.
        A2: Now also updates the context's last_response_hash.
        """
        if response.context_updated:
            # The response building method should have already updated the hash,
            # but this is a safeguard/confirmation.
            if response.response_hash is None:
                response.response_hash = hashlib.sha256(response.response.encode()).hexdigest()
            context.set_last_response_hash(response.response_hash)
            logger.debug(f"Finalized return: Context updated for {context.thread_id}/{context.node_id}/{context.objection_category}")
        return response

# ===== A1: Module-level convenience function (retained) =====
def handle_objection(thread_id: str, node_id: str, persona: str, objection_category: str, objection_type: str, user_utterance: str) -> Dict:
    """
    Module-level function to handle objections.
    Initializes a handler and processes the objection.
    """
    handler = ObjectionHandler(persona=persona)
    response_obj = handler.handle_objection(thread_id, node_id, objection_category, objection_type, user_utterance)
    
    # A2: Return a dictionary for broader compatibility and future expansion
    return {
        "response": response_obj.response,
        "response_type": response_obj.response_type,
        "context_updated": response_obj.context_updated,
        "occurrence": handler._get_context(thread_id, node_id, objection_category, objection_type).get_occurrence()
    }