"""
Real-time Conversation Analytics
"""
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class ConversationMetrics:
    """Tracks conversation metrics in real-time"""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_turns: int = 0
    user_turns: int = 0
    agent_turns: int = 0
    total_words: int = 0
    user_words: int = 0
    agent_words: int = 0
    avg_response_time: float = 0.0
    objection_count: int = 0
    conversion_events: List[str] = field(default_factory=list)
    personality_distribution: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    emotional_states: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    @property
    def duration(self) -> float:
        """Get conversation duration in seconds"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    @property
    def words_per_minute(self) -> float:
        """Get words per minute"""
        if self.duration > 0:
            return (self.total_words / self.duration) * 60
        return 0.0

class ConversationAnalytics:
    """Manages real-time conversation analytics"""
    
    def __init__(self):
        self.metrics = ConversationMetrics()
        self.turn_times = []
        
    def record_turn(self, speaker: str, text: str, response_time: Optional[float] = None):
        """
        Record a conversation turn
        
        Args:
            speaker (str): Who spoke ('user' or 'agent')
            text (str): What was said
            response_time (Optional[float]): Time taken to respond in seconds
        """
        self.metrics.total_turns += 1
        
        word_count = len(text.split())
        self.metrics.total_words += word_count
        
        if speaker == 'user':
            self.metrics.user_turns += 1
            self.metrics.user_words += word_count
        elif speaker == 'agent':
            self.metrics.agent_turns += 1
            self.metrics.agent_words += word_count
            
        if response_time is not None:
            self.turn_times.append(response_time)
            # Update average response time
            self.metrics.avg_response_time = sum(self.turn_times) / len(self.turn_times)
            
        logging.info(f"Recorded turn: {speaker} said {word_count} words")
        
    def record_objection(self):
        """Record an objection"""
        self.metrics.objection_count += 1
        logging.info("Recorded objection")
        
    def record_conversion_event(self, event: str):
        """
        Record a conversion event
        
        Args:
            event (str): Description of the conversion event
        """
        self.metrics.conversion_events.append(event)
        logging.info(f"Recorded conversion event: {event}")
        
    def record_personality(self, personality_type: str):
        """
        Record user personality type
        
        Args:
            personality_type (str): The personality type (D, I, S, C)
        """
        self.metrics.personality_distribution[personality_type] += 1
        logging.info(f"Recorded personality type: {personality_type}")
        
    def record_emotional_state(self, emotional_state: str):
        """
        Record user emotional state
        
        Args:
            emotional_state (str): The emotional state (positive, negative, neutral)
        """
        self.metrics.emotional_states[emotional_state] += 1
        logging.info(f"Recorded emotional state: {emotional_state}")
        
    def end_conversation(self):
        """Mark the end of the conversation"""
        self.metrics.end_time = time.time()
        logging.info("Conversation ended")
        
    def get_summary(self) -> Dict:
        """
        Get a summary of conversation metrics
        
        Returns:
            Dict: Summary of metrics
        """
        return {
            'duration_seconds': self.metrics.duration,
            'total_turns': self.metrics.total_turns,
            'user_turns': self.metrics.user_turns,
            'agent_turns': self.metrics.agent_turns,
            'total_words': self.metrics.total_words,
            'words_per_minute': self.metrics.words_per_minute,
            'avg_response_time': self.metrics.avg_response_time,
            'objection_count': self.metrics.objection_count,
            'conversion_events': self.metrics.conversion_events,
            'personality_distribution': dict(self.metrics.personality_distribution),
            'emotional_states': dict(self.metrics.emotional_states)
        }

# Global instance
conversation_analytics = ConversationAnalytics()