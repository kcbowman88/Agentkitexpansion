"""
Conversation State Manager
Manages the state of conversations including used strategies, context, and history.
"""
import logging
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from pivot_controller import PivotController # Import PivotController

class StrategyType(Enum):
    """Types of persuasion strategies"""
    DIRECT_VALUE = "direct_value"
    IMPACT_FOCUS = "impact_focus"
    SOCIAL_PROOF = "social_proof"
    LOGICAL_REASONING = "logical_reasoning"
    EMOTIONAL_APPEAL = "emotional_appeal"
    SCARCITY_URGENCY = "scarcity_urgency"
    AUTHORITY_CREDIBILITY = "authority_credibility"
    PROBLEM_AGITATION = "problem_agitation"
    FUTURE_PACING = "future_pacing"
    REFRAME_PERSPECTIVE = "reframe_perspective"

@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation"""
    speaker: str  # 'agent' or 'user'
    utterance: str
    timestamp: datetime = field(default_factory=datetime.now)
    node_id: Optional[str] = None
    strategy_used: Optional[str] = None
    objection_handled: Optional[str] = None
    interrupted: bool = False
    partial_chars: Optional[int] = None # Number of characters spoken before interruption

@dataclass
class NodeState:
    """Tracks the state of a specific node in the conversation"""
    node_id: str
    goal: str
    transition_conditions: Dict[str, str]
    attempts: int = 0
    strategies_used: Set[str] = field(default_factory=set)
    goal_achieved: bool = False
    last_user_input: Optional[str] = None

class ConversationStateManager:
    """
    Manages the complete state of a conversation including:
    - Conversation history
    - Used strategies (globally and per-node)
    - Current node state
    - User context and preferences
    - PivotController state
    """
    
    def __init__(self, max_history_size: int = 50, pivot_controller: Optional[PivotController] = None):
        self._history: List[ConversationTurn] = [] # Renamed to _history
        self.max_history_size = max_history_size
        self.global_strategies_used: Dict[str, List[str]] = {}  # objection -> strategies used
        self.current_node_state: Optional[NodeState] = None
        self.previous_node_states: List[NodeState] = []
        self.user_context: Dict[str, Any] = {}
        self.personality_type: str = 'S'  # Default DISC type
        self.objection_count: Dict[str, int] = {}  # Track how many times each objection appears
        self.flags: Dict[str, Any] = {} # General purpose flags
        self.pivot_controller = pivot_controller if pivot_controller is not None else PivotController() # Initialize PivotController

    @property
    def history(self) -> List[ConversationTurn]:
        """Public getter for conversation history."""
        return self._history
        
    def add_turn(self, speaker: str, utterance: str, node_id: Optional[str] = None,
                 strategy_used: Optional[str] = None, objection_handled: Optional[str] = None,
                 interrupted: bool = False, partial_chars: Optional[int] = None):
        """Add a conversation turn to history"""
        turn = ConversationTurn(
            speaker=speaker,
            utterance=utterance,
            node_id=node_id or (self.current_node_state.node_id if self.current_node_state else None),
            strategy_used=strategy_used,
            objection_handled=objection_handled,
            interrupted=interrupted,
            partial_chars=partial_chars
        )
        
        self._history.append(turn) # Use _history
        
        # Maintain max history size
        if len(self._history) > self.max_history_size:
            self._history.pop(0) # Use _history
            
        # Track strategies globally only if not interrupted
        if not interrupted and objection_handled and strategy_used:
            if objection_handled not in self.global_strategies_used:
                self.global_strategies_used[objection_handled] = []
            self.global_strategies_used[objection_handled].append(strategy_used)
            
            # Track objection frequency
            self.objection_count[objection_handled] = self.objection_count.get(objection_handled, 0) + 1
            
        # Update node state if applicable, only if not interrupted
        if not interrupted and self.current_node_state and strategy_used:
            self.current_node_state.strategies_used.add(strategy_used)
            
        if speaker == 'user' and self.current_node_state:
            self.current_node_state.last_user_input = utterance
            
        logging.info(f"Added turn: {speaker} - {utterance[:50]}... (Interrupted: {interrupted})")
        
    def record_strategy_use(self, objection: str, strategy: StrategyType):
        """
        Records that a strategy was used without adding a conversation turn.
        This is for cases where the agent's utterance might be interrupted.
        """
        if objection not in self.global_strategies_used:
            self.global_strategies_used[objection] = []
        self.global_strategies_used[objection].append(strategy.value)
        
        # Track objection frequency
        self.objection_count[objection] = self.objection_count.get(objection, 0) + 1
        
        if self.current_node_state:
            self.current_node_state.strategies_used.add(strategy.value)
        logging.info(f"Recorded strategy use: {strategy.value} for objection: {objection}")

    def set_current_node(self, node_id: str, goal: str, transition_conditions: Dict[str, str]):
        """Set the current node being processed"""
        # Save previous node state if exists
        if self.current_node_state:
            self.previous_node_states.append(self.current_node_state)
            
        self.current_node_state = NodeState(
            node_id=node_id,
            goal=goal,
            transition_conditions=transition_conditions
        )
        logging.info(f"Set current node: {node_id}")
        
    def increment_node_attempts(self):
        """Increment the attempt counter for the current node"""
        if self.current_node_state:
            self.current_node_state.attempts += 1
            logging.info(f"Node {self.current_node_state.node_id} attempts: {self.current_node_state.attempts}")
            
    def get_unused_strategies(self, objection: str) -> List[StrategyType]:
        """Get strategies that haven't been used for this objection"""
        used_strategies = set(self.global_strategies_used.get(objection, []))
        all_strategies = list(StrategyType)
        
        unused = [s for s in all_strategies if s.value not in used_strategies]
        logging.info(f"Unused strategies for '{objection}': {[s.value for s in unused]}")
        return unused
        
    def has_strategy_been_used(self, objection: str, strategy: str) -> bool:
        """Check if a specific strategy has been used for an objection"""
        return strategy in self.global_strategies_used.get(objection, [])
        
    def get_recent_history(self, num_turns: int = 6, include_interrupted: bool = True, mark_interrupted: bool = True) -> List[str]:
        """Get recent conversation history as formatted strings"""
        recent = self._history[-num_turns:] if self._history else [] # Use _history
        return [
            f"{turn.speaker.upper()}: {turn.utterance}{' [INTERRUPTED]' if turn.interrupted and mark_interrupted else ''}"
            for turn in recent if include_interrupted or not turn.interrupted
        ]
        
    def get_last_user_utterance(self) -> Optional[str]:
        """Get the most recent user utterance"""
        for turn in reversed(self._history): # Use _history
            if turn.speaker == 'user':
                return turn.utterance
        return None
        
    def get_last_agent_utterance(self) -> Optional[str]:
        """Get the most recent agent utterance"""
        for turn in reversed(self._history): # Use _history
            if turn.speaker == 'agent':
                return turn.utterance
        return None
        
    def update_user_context(self, key: str, value: Any):
        """Update user context information"""
        self.user_context[key] = value
        logging.info(f"Updated user context: {key} = {value}")
        
    def set_personality_type(self, disc_type: str):
        """Set the user's DISC personality type"""
        if disc_type in ['D', 'I', 'S', 'C']:
            self.personality_type = disc_type
            logging.info(f"Set personality type: {disc_type}")
            
    def should_escalate(self, max_attempts: int = 3) -> bool:
        """Determine if we should escalate to global prompt"""
        if not self.current_node_state:
            return False
            
        should_escalate = self.current_node_state.attempts >= max_attempts
        if should_escalate:
            logging.warning(f"Escalating after {self.current_node_state.attempts} attempts")
        return should_escalate
        
    def mark_goal_achieved(self):
        """Mark the current node's goal as achieved"""
        if self.current_node_state:
            self.current_node_state.goal_achieved = True
            logging.info(f"Goal achieved for node: {self.current_node_state.node_id}")
            
    def get_objection_frequency(self, objection: str) -> int:
        """Get how many times an objection has appeared"""
        return self.objection_count.get(objection, 0)
        
    def extract_user_statements(self) -> Dict[str, Any]:
        """Extract important statements from user for context integration"""
        statements = {
            'questions': [],
            'concerns': [],
            'interests': [],
            'objections': []
        }
        
        for turn in self._history: # Use _history
            if turn.speaker == 'user':
                utterance_lower = turn.utterance.lower()
                
                # Categorize user statements
                if '?' in turn.utterance:
                    statements['questions'].append(turn.utterance)
                elif any(word in utterance_lower for word in ['but', 'however', 'although']):
                    statements['concerns'].append(turn.utterance)
                elif any(word in utterance_lower for word in ['interested', 'like', 'want', 'need']):
                    statements['interests'].append(turn.utterance)
                elif turn.objection_handled:
                    statements['objections'].append(turn.utterance)
                    
        return statements
        
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation state"""
        return {
            'current_node': self.current_node_state.node_id if self.current_node_state else None,
            'node_attempts': self.current_node_state.attempts if self.current_node_state else 0,
            'total_turns': len(self._history), # Use _history
            'unique_objections': len(self.objection_count),
            'total_objections': sum(self.objection_count.values()),
            'personality_type': self.personality_type,
            'strategies_used_count': sum(len(strategies) for strategies in self.global_strategies_used.values())
        }
        
    def reset(self):
        """Reset the conversation state"""
        self._history.clear() # Use _history
        self.global_strategies_used.clear()
        self.current_node_state = None
        self.previous_node_states.clear()
        self.user_context.clear()
        self.personality_type = 'S'
        self.objection_count.clear()
        self.flags.clear()
        self.pivot_controller.reset_on_transition(None) # Reset pivot controller state
        logging.info("Conversation state reset")

    def set_flag(self, key: str, value: Any):
        """Set a general purpose flag in the state manager."""
        self.flags[key] = value
        logging.debug(f"Flag set: {key} = {value}")

    def get_flag(self, key: str, default: Any = None) -> Any:
        """Get a general purpose flag from the state manager."""
        return self.flags.get(key, default)

    def pop_flag(self, key: str, default: Any = None) -> Any:
        """Get and remove a general purpose flag from the state manager."""
        return self.flags.pop(key, default)


class StrategyTracker:
    """
    Tracks and manages strategy usage to prevent repetition
    """
    
    def __init__(self, state_manager: ConversationStateManager):
        self.state_manager = state_manager
        
    def get_next_strategy(self, objection: str, preferred_order: Optional[List[StrategyType]] = None) -> Optional[StrategyType]:
        """
        Get the next unused strategy for an objection
        
        Args:
            objection: The objection being handled
            preferred_order: Optional preferred order of strategies
            
        Returns:
            The next strategy to use, or None if all exhausted
        """
        unused_strategies = self.state_manager.get_unused_strategies(objection)
        
        if not unused_strategies:
            logging.warning(f"All strategies exhausted for objection: {objection}")
            return None
            
        # If preferred order provided, try to use it
        if preferred_order:
            for strategy in preferred_order:
                if strategy in unused_strategies:
                    return strategy
                    
        # Otherwise return the first unused
        return unused_strategies[0]
        
    # NOTE: This method is now deprecated. Strategy recording is handled directly by
    # ConversationStateManager.record_strategy_use after successful speech.
    # def record_strategy_use(self, objection: str, strategy: StrategyType):
    #     """Record that a strategy was used"""
    #     self.state_manager.add_turn(
    #         speaker='agent',
    #         utterance='',  # Will be filled by the actual response
    #         strategy_used=strategy.value,
    #         objection_handled=objection
    #     )
        
    def suggest_strategy_based_on_frequency(self, objection: str) -> StrategyType:
        """
        Suggest a strategy based on how many times the objection has appeared
        
        For repeated objections, escalate the strategy intensity
        """
        frequency = self.state_manager.get_objection_frequency(objection)
        
        # Strategy escalation based on repetition
        if frequency == 1:
            # First time - try gentle approach
            return StrategyType.DIRECT_VALUE
        elif frequency == 2:
            # Second time - appeal to impact
            return StrategyType.IMPACT_FOCUS
        elif frequency == 3:
            # Third time - use social proof
            return StrategyType.SOCIAL_PROOF
        elif frequency == 4:
            # Fourth time - future pacing
            return StrategyType.FUTURE_PACING
        else:
            # Fifth+ time - reframe completely
            return StrategyType.REFRAME_PERSPECTIVE
            
    def is_strategy_appropriate_for_personality(self, strategy: StrategyType, disc_type: str) -> bool:
        """
        Check if a strategy is appropriate for the user's personality type
        
        Based on DISC model:
        - D (Dominant): Responds to direct, results-focused approaches
        - I (Influential): Responds to social, enthusiastic approaches  
        - S (Steady): Responds to supportive, stable approaches
        - C (Conscientious): Responds to logical, detailed approaches
        """
        personality_strategy_map = {
            'D': [StrategyType.DIRECT_VALUE, StrategyType.LOGICAL_REASONING, 
                  StrategyType.SCARCITY_URGENCY, StrategyType.AUTHORITY_CREDIBILITY],
            'I': [StrategyType.SOCIAL_PROOF, StrategyType.EMOTIONAL_APPEAL,
                  StrategyType.FUTURE_PACING, StrategyType.IMPACT_FOCUS],
            'S': [StrategyType.IMPACT_FOCUS, StrategyType.SOCIAL_PROOF,
                  StrategyType.AUTHORITY_CREDIBILITY, StrategyType.REFRAME_PERSPECTIVE],
            'C': [StrategyType.LOGICAL_REASONING, StrategyType.AUTHORITY_CREDIBILITY,
                  StrategyType.PROBLEM_AGITATION, StrategyType.DIRECT_VALUE]
        }
        
        return strategy in personality_strategy_map.get(disc_type, [])
