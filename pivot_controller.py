"""PivotController centralizes pivot tracking and affirmative routing decisions.
It enforces a single pivot per user reply and provides signals used by higher-level
components to determine whether an affirmative should advance rather than retry.
"""
from __future__ import annotations
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

def _ends_with_question(text: str) -> bool:
    if text is None:
        return False
    return text.strip().endswith("?")

class PivotController:
    """
    Tracks pivot lifecycle across turns and exposes decisions for routing after affirmatives.

    Usage:
      - call register_bot_utterance(...) after the bot speaks
      - call register_user_turn(is_affirmative) on user input
      - check decision['should_advance'] to bypass retry loops
      - call reset_on_transition(next_node_id) after node changes
    """
    def __init__(self) -> None:
        self.last_bot_turn_ended_with_question: bool = False
        self.pivot_open: bool = False
        self.last_pivot_node_id: Optional[str] = None
        self.just_advanced_on_pivot: bool = False

    def register_bot_utterance(self, text: str, node_id: Optional[str], ended_with_question: Optional[bool] = None) -> None:
        """
        Record the last bot utterance and whether it ended with a question (a pivot).
        If ended_with_question is explicitly provided, it overrides the automatic detection.
        """
        if ended_with_question is not None:
            ended = ended_with_question
        else:
            ended = _ends_with_question(text or "")
        
        self.last_bot_turn_ended_with_question = ended
        self.pivot_open = ended
        self.last_pivot_node_id = node_id if ended else None
        logger.info(
            "PivotController.register_bot_utterance node=%s ended_with_question=%s (explicit: %s)",
            node_id, ended, ended_with_question is not None
        )

    def pivot_started(self, node_id: Optional[str]) -> None:
        """
        Explicitly mark that a pivot was emitted for the current bot turn.
        """
        self.pivot_open = True
        self.last_pivot_node_id = node_id
        self.last_bot_turn_ended_with_question = True
        logger.info("PivotController.pivot_started node=%s", node_id)

    def pivot_completed(self) -> None:
        """
        Mark the end of pivot emission for the current bot turn.
        """
        self.pivot_open = False
        logger.info("PivotController.pivot_completed node=%s", self.last_pivot_node_id)

    def register_user_turn(self, is_affirmative: bool) -> Dict[str, object]:
        """
        Called when a user input is finalized. Returns a decision dict. This method is idempotent
        within a single turn; once it decides to advance, it will continue to do so until reset.
        """
        # If we already decided to advance on this turn, stick with that decision.
        if self.just_advanced_on_pivot:
            return {
                "should_advance": True,
                "reason": "affirmative_after_pivot",
                "last_pivot_node_id": self.last_pivot_node_id,
            }

        should_advance = self.last_bot_turn_ended_with_question and is_affirmative
        reason = "affirmative_after_pivot" if should_advance else "no_pivot_or_not_affirmative"

        decision = {
            "should_advance": should_advance,
            "reason": reason,
            "last_pivot_node_id": self.last_pivot_node_id,
        }

        logger.info(
            "PivotController.register_user_turn is_affirmative=%s last_bot_turn_ended_with_question=%s decision=%s",
            is_affirmative, self.last_bot_turn_ended_with_question, reason
        )

        if should_advance:
            self.just_advanced_on_pivot = True # Latch the decision

        # Reset the question flag now, but the latched decision will persist until a node transition.
        self.last_bot_turn_ended_with_question = False

        return decision

    def reset_on_transition(self, next_node_id: Optional[str]) -> None:
        """
        Reset internal flags after a node transition occurs. This is the only
        time the 'just_advanced_on_pivot' latch should be cleared.
        """
        logger.info(
            "PivotController.reset_on_transition next_node=%s (clearing pivot state)",
            next_node_id,
        )
        self.pivot_open = False
        self.last_pivot_node_id = None
        self.last_bot_turn_ended_with_question = False
        self.just_advanced_on_pivot = False # Crucially, reset the latch here.

# Provide a module-level singleton for convenience where DI isn't wired.
pivot_controller = PivotController()