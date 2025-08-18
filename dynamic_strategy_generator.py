"""
Dynamic Strategy Generator
Generates fundamentally different persuasion strategies for objection handling.
"""
import logging
import random
from typing import Dict, List, Optional, Tuple
from enum import Enum
from conversation_state_manager import StrategyType

class StrategyTemplate:
    """Template for generating strategy-specific responses"""
    
    def __init__(self, strategy_type: StrategyType, 
                 templates: List[str], 
                 follow_up_questions: List[str]):
        self.strategy_type = strategy_type
        self.templates = templates
        self.follow_up_questions = follow_up_questions
        
    def generate(self, context: Dict[str, str]) -> str:
        """Generate a response using this strategy"""
        template = random.choice(self.templates)
        question = random.choice(self.follow_up_questions)
        
        # Fill in context variables
        response = template.format(**context)
        return f"{response} {question}"

class DynamicStrategyGenerator:
    """
    Generates fundamentally different approaches to achieve the same goal
    """
    
    def __init__(self):
        self.strategy_templates = self._initialize_strategy_templates()
        self.objection_strategies = self._initialize_objection_strategies()
        
    def _initialize_strategy_templates(self) -> Dict[StrategyType, StrategyTemplate]:
        """Initialize templates for each strategy type"""
        return {
            StrategyType.DIRECT_VALUE: StrategyTemplate(
                StrategyType.DIRECT_VALUE,
                templates=[
                    "It's pretty straightforward - we build sites that generate {income_amount} monthly.",
                    "Simply put, this creates {income_amount} in passive income.",
                    "The model generates {income_amount} per month, plain and simple."
                ],
                follow_up_questions=[
                    "Would you be upset with an extra {income_amount} a month?",
                    "Is {income_amount} monthly something you'd want?",
                    "Would {income_amount} extra each month help?"
                ]
            ),
            
            StrategyType.IMPACT_FOCUS: StrategyTemplate(
                StrategyType.IMPACT_FOCUS,
                templates=[
                    "Think about what {income_amount} monthly would mean for your family.",
                    "Imagine not worrying about bills with {income_amount} coming in.",
                    "Picture having {income_amount} extra without working more hours."
                ],
                follow_up_questions=[
                    "How would that change things for you?",
                    "What would you do with that freedom?",
                    "Would that solve your biggest challenge?"
                ]
            ),
            
            StrategyType.SOCIAL_PROOF: StrategyTemplate(
                StrategyType.SOCIAL_PROOF,
                templates=[
                    "We've helped over {student_count} people reach {income_amount} monthly.",
                    "Just last month, {success_story} started making {income_amount}.",
                    "{student_count} students are already at {income_amount} per month."
                ],
                follow_up_questions=[
                    "What would need to be true for you to believe you could too?",
                    "If they can do it, why not you?",
                    "Want to hear how they did it?"
                ]
            ),
            
            StrategyType.LOGICAL_REASONING: StrategyTemplate(
                StrategyType.LOGICAL_REASONING,
                templates=[
                    "Each site generates {site_income}, multiply by 10 sites, that's {income_amount}.",
                    "The math is simple: {calculation} equals {income_amount} monthly.",
                    "Google gets {search_volume} searches, even 1% conversion means {income_amount}."
                ],
                follow_up_questions=[
                    "Does that math make sense to you?",
                    "Can you see how the numbers add up?",
                    "Is there a flaw in that logic?"
                ]
            ),
            
            StrategyType.EMOTIONAL_APPEAL: StrategyTemplate(
                StrategyType.EMOTIONAL_APPEAL,
                templates=[
                    "I remember when I was skeptical too, before seeing {income_amount} hit my account.",
                    "The relief of having {income_amount} coming in changed everything for me.",
                    "That first {income_amount} month was when I knew my family was secure."
                ],
                follow_up_questions=[
                    "Can you relate to that feeling?",
                    "Wouldn't that peace of mind be worth it?",
                    "How would you feel seeing that in your account?"
                ]
            ),
            
            StrategyType.SCARCITY_URGENCY: StrategyTemplate(
                StrategyType.SCARCITY_URGENCY,
                templates=[
                    "We only have {spots_left} spots this month for {income_amount} potential.",
                    "The {income_amount} opportunity closes in {time_left}.",
                    "Markets getting saturated - {income_amount} is easier now than later."
                ],
                follow_up_questions=[
                    "Do you want to miss this window?",
                    "Should we lock in your spot?",
                    "Can you afford to wait?"
                ]
            ),
            
            StrategyType.AUTHORITY_CREDIBILITY: StrategyTemplate(
                StrategyType.AUTHORITY_CREDIBILITY,
                templates=[
                    "As a software engineer, I verified the {income_amount} model myself.",
                    "Our CEO built this after making {income_amount} monthly for 5 years.",
                    "Featured in {publication} for helping people reach {income_amount}."
                ],
                follow_up_questions=[
                    "Does that credibility matter to you?",
                    "Would you trust that expertise?",
                    "Is proven success important?"
                ]
            ),
            
            StrategyType.PROBLEM_AGITATION: StrategyTemplate(
                StrategyType.PROBLEM_AGITATION,
                templates=[
                    "Without {income_amount} extra, how long can you keep struggling?",
                    "Every month without {income_amount} is money left on the table.",
                    "While you wait, others are making {income_amount}."
                ],
                follow_up_questions=[
                    "How much longer will you accept that?",
                    "What's the cost of not acting?",
                    "Can you afford the status quo?"
                ]
            ),
            
            StrategyType.FUTURE_PACING: StrategyTemplate(
                StrategyType.FUTURE_PACING,
                templates=[
                    "Six months from now, you could have {income_amount} monthly automated.",
                    "By next year, {income_amount} could be your new normal.",
                    "Imagine looking back, grateful you started the {income_amount} journey today."
                ],
                follow_up_questions=[
                    "Where do you see yourself then?",
                    "Is that future worth 25 seconds now?",
                    "Will you regret not exploring this?"
                ]
            ),
            
            StrategyType.REFRAME_PERSPECTIVE: StrategyTemplate(
                StrategyType.REFRAME_PERSPECTIVE,
                templates=[
                    "It's not about the work, it's about building {income_amount} in assets.",
                    "Think of it as buying a {income_amount} monthly annuity.",
                    "This isn't a job, it's creating {income_amount} in passive ownership."
                ],
                follow_up_questions=[
                    "Does that shift how you see it?",
                    "Makes more sense that way, right?",
                    "Can you see the difference?"
                ]
            )
        }
        
    def _initialize_objection_strategies(self) -> Dict[str, List[StrategyType]]:
        """Map objections to preferred strategy order"""
        return {
            "busy": [
                StrategyType.IMPACT_FOCUS,
                StrategyType.FUTURE_PACING,
                StrategyType.PROBLEM_AGITATION,
                StrategyType.REFRAME_PERSPECTIVE
            ],
            "not interested": [
                StrategyType.DIRECT_VALUE,
                StrategyType.SOCIAL_PROOF,
                StrategyType.EMOTIONAL_APPEAL,
                StrategyType.SCARCITY_URGENCY
            ],
            "skeptical": [
                StrategyType.LOGICAL_REASONING,
                StrategyType.SOCIAL_PROOF,
                StrategyType.AUTHORITY_CREDIBILITY,
                StrategyType.DIRECT_VALUE
            ],
            "no money": [
                StrategyType.PROBLEM_AGITATION,
                StrategyType.FUTURE_PACING,
                StrategyType.IMPACT_FOCUS,
                StrategyType.REFRAME_PERSPECTIVE
            ],
            "need to think": [
                StrategyType.SCARCITY_URGENCY,
                StrategyType.SOCIAL_PROOF,
                StrategyType.FUTURE_PACING,
                StrategyType.LOGICAL_REASONING
            ]
        }
        
    def generate_strategy_response(self, 
                                  objection: str,
                                  strategy_type: StrategyType,
                                  context: Dict[str, str]) -> str:
        """
        Generate a response using a specific strategy
        
        Args:
            objection: The objection being handled
            strategy_type: The strategy to use
            context: Context variables for the templates
            
        Returns:
            Generated response using the strategy
        """
        # Set default context values
        default_context = {
            'income_amount': '$20k',
            'student_count': '7,500',
            'site_income': '$2k',
            'calculation': '10 sites x $2k',
            'search_volume': '8.5 billion',
            'spots_left': '3',
            'time_left': '48 hours',
            'publication': 'Forbes',
            'success_story': 'John from Texas'
        }
        
        # Merge with provided context
        full_context = {**default_context, **context}
        
        # Get the strategy template
        template = self.strategy_templates.get(strategy_type)
        
        if not template:
            logging.warning(f"No template for strategy: {strategy_type}")
            return "Let me put it another way."
            
        # Generate response
        response = template.generate(full_context)
        
        # Add objection-specific adjustments
        response = self._adjust_for_objection(response, objection)
        
        return response
        
    def _adjust_for_objection(self, response: str, objection: str) -> str:
        """Adjust response based on specific objection"""
        objection_lower = objection.lower()
        
        if 'busy' in objection_lower:
            # Add time acknowledgment
            prefix = random.choice([
                "I know you're busy, so here's the thing -",
                "For busy people specifically,",
                "This is designed for busy people -"
            ])
            return f"{prefix} {response}"
            
        elif 'not interested' in objection_lower:
            # Add interest reframe
            prefix = random.choice([
                "I get it, but consider this -",
                "Fair enough, but what if",
                "I understand, just think about this -"
            ])
            return f"{prefix} {response}"
            
        elif 'scam' in objection_lower or 'trust' in objection_lower:
            # Add credibility
            prefix = random.choice([
                "I understand the skepticism.",
                "Trust is earned, I get it.",
                "That's a smart concern."
            ])
            return f"{prefix} {response}"
            
        return response
        
    def get_strategy_sequence(self, objection: str) -> List[StrategyType]:
        """
        Get the recommended sequence of strategies for an objection
        
        Args:
            objection: The objection to handle
            
        Returns:
            Ordered list of strategies to try
        """
        objection_lower = objection.lower()
        
        # Find matching objection pattern
        for key, strategies in self.objection_strategies.items():
            if key in objection_lower:
                return strategies
                
        # Default sequence if no match
        return [
            StrategyType.DIRECT_VALUE,
            StrategyType.IMPACT_FOCUS,
            StrategyType.SOCIAL_PROOF,
            StrategyType.FUTURE_PACING,
            StrategyType.REFRAME_PERSPECTIVE
        ]
        
    def generate_pivot_question(self, node_goal: str, attempt_number: int) -> str:
        """
        Generate a pivot question to achieve the node goal
        
        Args:
            node_goal: The goal to achieve
            attempt_number: Which attempt this is
            
        Returns:
            A question designed to achieve the goal
        """
        # Different approaches based on attempt number
        if attempt_number == 1:
            # Direct approach
            questions = [
                "So would an extra $20k a month work for you?",
                "Is $20k monthly something you'd want?",
                "Would $20k extra each month help your situation?"
            ]
        elif attempt_number == 2:
            # Impact approach
            questions = [
                "How would an extra $20k monthly change your life?",
                "What would $20k a month mean for your family?",
                "Where would you be with $20k more each month?"
            ]
        elif attempt_number == 3:
            # Challenge approach
            questions = [
                "What's stopping you from wanting $20k more monthly?",
                "Why wouldn't you want an extra $20k each month?",
                "Is there a downside to $20k monthly I'm missing?"
            ]
        else:
            # Final approach - assumptive
            questions = [
                "When you start seeing that $20k monthly, what's first?",
                "Once the $20k is flowing, what changes?",
                "The $20k monthly - checking or savings account?"
            ]
            
        return random.choice(questions)
        
    def create_unique_angle(self, previous_angles: List[str], goal: str) -> str:
        """
        Create a unique angle that hasn't been used before
        
        Args:
            previous_angles: List of angles already tried
            goal: The goal to achieve
            
        Returns:
            A fresh angle to approach the goal
        """
        all_angles = [
            "value",  # Focus on the monetary value
            "time",  # Focus on time freedom
            "family",  # Focus on family impact
            "security",  # Focus on financial security
            "opportunity",  # Focus on missing out
            "comparison",  # Compare to others' success
            "logic",  # Use logical reasoning
            "emotion",  # Appeal to emotions
            "authority",  # Use credibility
            "simplicity",  # Emphasize how easy it is
            "lifestyle",  # Focus on lifestyle change
            "problem",  # Agitate current problems
            "future",  # Paint future picture
            "ownership",  # Focus on owning assets
            "passive",  # Emphasize passive nature
        ]
        
        # Find unused angles
        unused = [a for a in all_angles if a not in previous_angles]
        
        if not unused:
            # All angles used, combine two
            angle1 = random.choice(all_angles)
            angle2 = random.choice([a for a in all_angles if a != angle1])
            return f"{angle1}+{angle2}"
            
        return random.choice(unused)