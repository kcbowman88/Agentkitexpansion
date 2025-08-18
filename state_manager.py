from dataclasses import dataclass, field
from typing import Optional
from disc_classifier import DISCProfile

@dataclass
class CallFlowState:
    customer_name: str = ""
    current_node_id: str = "N001A_NameConfirmation_Only"
    disc_profile: Optional[DISCProfile] = None
    emotional_state: Optional[str] = None
    objection_history: list = field(default_factory=list)
    conversation_context: dict = field(default_factory=dict)
    user_preferences: dict = field(default_factory=dict)
    conversation_history: list = field(default_factory=list)
    thread_id: Optional[str] = None
    waiting_for_objection_response: bool = False
    agent_utterance_history: list = field(default_factory=list)
    interruption_count: int = 0
    tactic_history: dict = field(default_factory=dict) # Tracks tactics used per node
    user_income: Optional[float] = None # Track user's stated income
    has_discussed_income_potential: bool = False