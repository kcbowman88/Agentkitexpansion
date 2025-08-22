from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from new_call_system.models import DISCProfile

@dataclass
class ConversationState:
    """Manages all state for a single call conversation."""
    customer_name: str
    current_node_id: str
    disc_profile: Optional[DISCProfile] = None
    utterance_history: List[Dict[str, str]] = field(default_factory=list)
    interruption_count: int = 0
    tactic_history: Dict[str, List[str]] = field(default_factory=dict)

    # Financial qualification data
    yearly_income: Optional[int] = None
    monthly_revenue: Optional[int] = None
    side_hustle_income: Optional[int] = None
    has_capital: Optional[bool] = None
    credit_score: Optional[int] = None

    # Scheduling data
    partner_involved: bool = False
    appointment_time: Optional[str] = None

    # Flags
    waiting_for_objection_response: bool = False
    last_agent_interrupted: bool = False

    def log_utterance(self, speaker: str, utterance: str, node_id: str, interrupted: bool = False):
        """Adds an utterance to the history."""
        self.utterance_history.append({
            "speaker": speaker,
            "utterance": utterance,
            "node_id": node_id,
            "interrupted": interrupted,
        })

    def add_tactic_to_history(self, node_id: str, tactic_name: str):
        """Records that a tactic has been used for a specific node."""
        if node_id not in self.tactic_history:
            self.tactic_history[node_id] = []
        self.tactic_history[node_id].append(tactic_name)

    def has_used_tactic(self, node_id: str, tactic_name: str) -> bool:
        """Checks if a tactic has already been used for a node."""
        return tactic_name in self.tactic_history.get(node_id, [])
