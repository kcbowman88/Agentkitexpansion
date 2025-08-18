"""
Tactical Response System
Implements constrained response generation with pre-scripted tactical options
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random
import logging

@dataclass
class TacticalResponse:
    """Represents a tactical response option"""
    id: str
    text: str
    category: str
    priority: int
    personality_adapted: bool = False

class TacticalResponder:
    """Manages tactical responses for different conversation scenarios"""
    
    def __init__(self):
        # Initialize tactical response libraries
        self.tactical_responses = {
            "acknowledgment": self._get_acknowledgment_responses(),
            "objection_handling": self._get_objection_handling_responses(),
            "value_proposition": self._get_value_proposition_responses(),
            "transition_prompts": self._get_transition_prompts(),
            "closing_techniques": self._get_closing_techniques()
        }
        
        # Track used tactics to prevent repetition
        self.used_tactics = set()

    def get_tactical_response(self, category: str, personality_type: str = "S", 
                            context: Optional[Dict] = None) -> Optional[TacticalResponse]:
        """
        Get a tactical response for a specific category
        
        Args:
            category (str): The category of response needed
            personality_type (str): The user's DISC personality type
            context (Dict): Additional context for response selection
            
        Returns:
            Optional[TacticalResponse]: A tactical response or None if not found
        """
        if category not in self.tactical_responses:
            return None
            
        # Filter out already used tactics
        available_responses = [
            resp for resp in self.tactical_responses[category] 
            if resp.id not in self.used_tactics
        ]
        
        if not available_responses:
            # If all tactics have been used, reset and allow repetition
            available_responses = self.tactical_responses[category]
            self.used_tactics.clear()
            
        # Adapt response to personality type if needed
        adapted_responses = [
            resp for resp in available_responses 
            if resp.personality_adapted or self._is_suitable_for_personality(resp, personality_type)
        ]
        
        if adapted_responses:
            # Select a random response from suitable options
            selected_response = random.choice(adapted_responses)
            self.used_tactics.add(selected_response.id)
            return selected_response
            
        return None

    def _get_acknowledgment_responses(self) -> List[TacticalResponse]:
        """Get acknowledgment responses"""
        return [
            TacticalResponse("ack_1", "Okay.", "acknowledgment", 1),
            TacticalResponse("ack_2", "Right.", "acknowledgment", 1),
            TacticalResponse("ack_3", "Got it.", "acknowledgment", 1),
            TacticalResponse("ack_4", "I see.", "acknowledgment", 1),
            TacticalResponse("ack_5", "Understood.", "acknowledgment", 1),
            TacticalResponse("ack_6", "That's clear.", "acknowledgment", 1),
            TacticalResponse("ack_7", "I get that.", "acknowledgment", 2, True),
            TacticalResponse("ack_8", "Makes sense.", "acknowledgment", 2, True),
            TacticalResponse("ack_9", "I can see that.", "acknowledgment", 2, True),
            TacticalResponse("ack_10", "Good.", "acknowledgment", 3, True),
            TacticalResponse("ack_11", "Perfect.", "acknowledgment", 3, True),
            TacticalResponse("ack_12", "Excellent.", "acknowledgment", 3, True),
            TacticalResponse("ack_13", "Interesting. So,", "acknowledgment", 4, True),
            TacticalResponse("ack_14", "Alright. Well,", "acknowledgment", 4, True)
        ]

    def _get_objection_handling_responses(self) -> List[TacticalResponse]:
        """Get objection handling responses"""
        return [
            TacticalResponse("obj_1", "Let me ask you something - what would need to change for this to be something you'd consider?", "objection_handling", 1),
            TacticalResponse("obj_2", "I appreciate you sharing that concern. Many of our successful students had similar initial thoughts.", "objection_handling", 2),
            TacticalResponse("obj_3", "That's a fair point. What I've found is that...", "objection_handling", 2),
            TacticalResponse("obj_4", "I understand where you're coming from. Let me share what we've seen with other students...", "objection_handling", 3),
            TacticalResponse("obj_5", "You know what, that's exactly why we've structured our program the way we have...", "objection_handling", 3),
            TacticalResponse("obj_6", "I hear you, and I want to address that directly...", "objection_handling", 2),
            TacticalResponse("obj_7", "That's actually a common question. What we've found is...", "objection_handling", 2),
            TacticalResponse("obj_8", "I'm glad you brought that up. Many people think that way initially, but then they discover...", "objection_handling", 3)
        ]

    def _get_value_proposition_responses(self) -> List[TacticalResponse]:
        """Get value proposition responses"""
        return [
            TacticalResponse("val_1", "What I love about this opportunity is...", "value_proposition", 1),
            TacticalResponse("val_2", "The reason I'm excited to share this with you is...", "value_proposition", 2),
            TacticalResponse("val_3", "Here's what makes this different from other opportunities...", "value_proposition", 2),
            TacticalResponse("val_4", "What I've seen our students achieve is truly remarkable...", "value_proposition", 3),
            TacticalResponse("val_5", "The potential here is significant - let me show you what's possible...", "value_proposition", 3),
            TacticalResponse("val_6", "This isn't just about making money - it's about creating freedom...", "value_proposition", 2),
            TacticalResponse("val_7", "What sets this apart is the proven system behind it...", "value_proposition", 2),
            TacticalResponse("val_8", "The beauty of this model is how it works with your current situation...", "value_proposition", 1)
        ]

    def _get_transition_prompts(self) -> List[TacticalResponse]:
        """Get transition prompts"""
        return [
            TacticalResponse("trans_1", "With that in mind, what are your thoughts?", "transition_prompts", 1),
            TacticalResponse("trans_2", "How does that align with what you're looking for?", "transition_prompts", 1),
            TacticalResponse("trans_3", "What questions come to mind as you hear this?", "transition_prompts", 2),
            TacticalResponse("trans_4", "I'm curious about your perspective on this...", "transition_prompts", 2),
            TacticalResponse("trans_5", "Does this sound like something that could work for you?", "transition_prompts", 1),
            TacticalResponse("trans_6", "What's your initial reaction to what I've shared?", "transition_prompts", 2),
            TacticalResponse("trans_7", "Is this the kind of opportunity you've been looking for?", "transition_prompts", 1),
            TacticalResponse("trans_8", "How does this compare to what you've considered before?", "transition_prompts", 2)
        ]

    def _get_closing_techniques(self) -> List[TacticalResponse]:
        """Get closing techniques"""
        return [
            TacticalResponse("close_1", "Would you like to explore this further?", "closing_techniques", 1),
            TacticalResponse("close_2", "Does this sound like something worth discussing in more detail?", "closing_techniques", 1),
            TacticalResponse("close_3", "What would it take for you to move forward with this?", "closing_techniques", 2),
            TacticalResponse("close_4", "If we could address your main concerns, would you be open to taking the next step?", "closing_techniques", 3),
            TacticalResponse("close_5", "Is this something you'd like to learn more about?", "closing_techniques", 1),
            TacticalResponse("close_6", "How soon would you like to get started?", "closing_techniques", 2),
            TacticalResponse("close_7", "When would be a good time to dive deeper into this?", "closing_techniques", 2),
            TacticalResponse("close_8", "What's the next logical step for you here?", "closing_techniques", 2)
        ]

    def _is_suitable_for_personality(self, response: TacticalResponse, personality_type: str) -> bool:
        """
        Check if a response is suitable for a specific personality type
        
        Args:
            response (TacticalResponse): The response to check
            personality_type (str): The DISC personality type
            
        Returns:
            bool: Whether the response is suitable
        """
        # For now, we'll make all responses available but track personality adaptation
        # In a more advanced implementation, we would filter based on personality type
        return True

    def get_patient_listening_prompt(self) -> str:
        """
        Get a prompt for patient listening
        
        Returns:
            str: A patient listening prompt
        """
        return "I'm going to pause here to give you a moment to think about that. Take your time..."

    def get_ambiguity_handling_response(self) -> str:
        """
        Get a response for handling ambiguous user input
        
        Returns:
            str: An ambiguity handling response
        """
        ambiguity_responses = [
            "I want to make sure I understand you correctly. Could you tell me a bit more about what you mean?",
            "I'm not sure I caught that completely. Could you clarify what you're thinking?",
            "I want to make sure I'm addressing your exact question. Could you elaborate on that point?",
            "I want to be sure I'm following you. Could you say that one more time?",
            "I want to make sure I'm giving you the right information. Could you help me understand your question better?"
        ]
        return random.choice(ambiguity_responses)

    def reset_tactics(self):
        """Reset the used tactics tracking"""
        self.used_tactics.clear()
