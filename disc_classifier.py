"""
DISC Personality Classification System
Analyzes user responses to categorize them as Dominant, Influential, Steady, or Conscientious
"""
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class DISCProfile:
    """Represents a DISC personality profile"""
    type: str
    confidence: float
    indicators: List[str]

class DISCClassifier:
    """Classifies user responses according to DISC personality types"""
    
    def __init__(self):
        # Define key indicators for each DISC type based on the Disc Comprehensive Guide
        self.disc_indicators = {
            'D': [  # Dominance
                r'\b(?:decisive|direct|quick|fast|immediate|now|urgent|control|lead|manage)\b',
                r'\b(?:don\'t have time|busy|efficient|results|bottom line|what\'s in it|benefit)\b',
                r'\b(?:tell me|what|how much|when|why|explain)\b',
                r'\b(?:guarantee|risk|proof|evidence|data)\b'
            ],
            'I': [  # Influence
                r'\b(?:fun|exciting|interesting|cool|awesome|amazing|wow)\b',
                r'\b(?:together|team|people|social|friends|network|community)\b',
                r'\b(?:story|experience|example|testimony|witness)\b',
                r'\b(?:love|like|enjoy|passion|enthusiastic)\b'
            ],
            'S': [  # Steadiness
                r'\b(?:stable|consistent|reliable|dependable|predictable|secure)\b',
                r'\b(?:family|friend|relationship|harmony|peace|comfortable)\b',
                r'\b(?:step by step|gradually|carefully|slowly|thoroughly)\b',
                r'\b(?:help|support|assist|cooperate|collaborate)\b'
            ],
            'C': [  # Conscientiousness
                r'\b(?:accurate|precise|exact|detailed|specific|technical)\b',
                r'\b(?:data|facts|evidence|proof|research|analysis|logic)\b',
                r'\b(?:process|procedure|system|method|approach|framework)\b',
                r'\b(?:question|concern|issue|problem|challenge|obstacle)\b'
            ]
        }
        
        # Behavioral patterns for each type
        self.behavioral_patterns = {
            'D': {
                'response_style': 'curt, one word answers, may be rude, cuts you off',
                'communication': 'direct, fast-paced, assertive, dynamic, bold',
                'motivations': 'power, authority, competition, winning, success',
                'fears': 'loss of control, being taken advantage of, vulnerability'
            },
            'I': {
                'response_style': 'jumps right into rapport, high energy, long rants',
                'communication': 'open, expressive, enthusiastic, people-focused',
                'motivations': 'social recognition, group activities, friendly relationships',
                'fears': 'social rejection, disapproval, loss of influence, being ignored'
            },
            'S': {
                'response_style': 'chill, warm, normal, reluctant to build rapport',
                'communication': 'indirect, open, calm, methodical, team-focused',
                'motivations': 'stable environments, sincere appreciation, cooperation',
                'fears': 'loss of stability, change, loss of harmony, offending others'
            },
            'C': {
                'response_style': 'questions, details, reluctant to build rapport',
                'communication': 'indirect, guarded, logical, analytical, detail-oriented',
                'motivations': 'accuracy, expertise, knowledge, quality, process',
                'fears': 'criticism, slipshod methods, being wrong, illogical acts'
            }
        }

    def classify_response(self, response: str) -> DISCProfile:
        """
        Classify a user response into a DISC personality type
        
        Args:
            response (str): The user's response text
            
        Returns:
            DISCProfile: The classified personality type with confidence and indicators
        """
        # Convert to lowercase for matching
        response_lower = response.lower()
        
        # Count matches for each DISC type
        type_scores = {}
        type_indicators = {}
        
        for disc_type, patterns in self.disc_indicators.items():
            matches = []
            score = 0
            
            for pattern in patterns:
                found_matches = re.findall(pattern, response_lower)
                if found_matches:
                    matches.extend(found_matches)
                    score += len(found_matches)
            
            type_scores[disc_type] = score
            type_indicators[disc_type] = matches
        
        # Determine the primary type
        if not any(type_scores.values()):
            # If no clear indicators, return neutral
            return DISCProfile(
                type='S',  # Default to Steady as neutral
                confidence=0.5,
                indicators=[]
            )
        
        primary_type = max(type_scores, key=type_scores.get)
        max_score = type_scores[primary_type]
        
        # Calculate confidence (0.5 to 1.0)
        total_score = sum(type_scores.values())
        confidence = 0.5 + (max_score / total_score) * 0.5 if total_score > 0 else 0.5
        
        return DISCProfile(
            type=primary_type,
            confidence=confidence,
            indicators=type_indicators[primary_type]
        )
    
    def classify_with_sentiment(self, response: str, sentiment_score: float) -> DISCProfile:
        """
        Classify a user response into a DISC personality type, considering sentiment analysis
        
        Args:
            response (str): The user's response text
            sentiment_score (float): Sentiment score from -1 (negative) to 1 (positive)
            
        Returns:
            DISCProfile: The classified personality type with confidence and indicators
        """
        # Get base classification
        base_profile = self.classify_response(response)
        
        # Adjust classification based on sentiment
        # Influential types tend to have more positive sentiment
        # Conscientious types tend to have more negative sentiment (critical)
        # Steady types tend to have neutral sentiment
        # Dominant types can have varied sentiment but often direct
        
        if base_profile.type == 'I' and sentiment_score > 0.5:
            # Reinforce Influential classification for positive responses
            base_profile.confidence = min(1.0, base_profile.confidence + 0.1)
        elif base_profile.type == 'C' and sentiment_score < -0.3:
            # Reinforce Conscientious classification for negative/critical responses
            base_profile.confidence = min(1.0, base_profile.confidence + 0.1)
        elif base_profile.type == 'D' and abs(sentiment_score) > 0.3:
            # Reinforce Dominant classification for strong sentiment (positive or negative)
            base_profile.confidence = min(1.0, base_profile.confidence + 0.1)
            
        return base_profile
    
    def get_adaptive_response_strategy(self, disc_type: str) -> Dict[str, str]:
        """
        Get adaptive response strategies based on DISC type
        
        Args:
            disc_type (str): The DISC personality type
            
        Returns:
            Dict[str, str]: Response strategy guidelines
        """
        strategies = {
            'D': {
                'approach': 'Be direct, focus on results, efficiency, and control',
                'language': 'Use decisive language, focus on outcomes and benefits',
                'pace': 'Fast-paced, get to the point quickly',
                'objection_handling': 'Address concerns directly, provide options'
            },
            'I': {
                'approach': 'Be enthusiastic, focus on recognition and social aspects',
                'language': 'Use expressive language, tell stories and examples',
                'pace': 'Energetic, allow for rapport building',
                'objection_handling': 'Use positive reframing, social proof'
            },
            'S': {
                'approach': 'Be calm, focus on stability, security, and cooperation',
                'language': 'Use reassuring language, emphasize teamwork',
                'pace': 'Slower, step-by-step approach',
                'objection_handling': 'Provide reassurance, address concerns patiently'
            },
            'C': {
                'approach': 'Be logical, focus on accuracy, details, and process',
                'language': 'Use precise language, provide data and evidence',
                'pace': 'Systematic, thorough explanations',
                'objection_handling': 'Provide detailed answers, logical reasoning'
            }
        }
        
        return strategies.get(disc_type, strategies['S'])  # Default to Steady

    def update_classification_with_context(self, current_profile: DISCProfile, 
                                         context_indicators: List[str]) -> DISCProfile:
        """
        Update classification based on conversation context
        
        Args:
            current_profile (DISCProfile): Current personality profile
            context_indicators (List[str]): Additional context indicators
            
        Returns:
            DISCProfile: Updated personality profile
        """
        # This method would be used to refine classification based on conversation history
        # For now, we'll return the current profile
        return current_profile
