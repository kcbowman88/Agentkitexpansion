"""
Context Integrator
Smoothly integrates user context and statements into agent responses.
"""
import logging
import random
from typing import Dict, List, Optional, Tuple
from enum import Enum

class IntegrationStyle(Enum):
    """Different styles of context integration"""
    ACKNOWLEDGE = "acknowledge"  # Brief acknowledgment
    ANSWER = "answer"  # Direct answer to question
    WEAVE = "weave"  # Weave into main response
    BRIDGE = "bridge"  # Use as bridge to next point
    IGNORE = "ignore"  # Strategically ignore
    EMPATHIZE = "empathize"  # Show understanding
    REFRAME = "reframe"  # Reframe their statement

class ContextIntegrator:
    """
    Integrates user context naturally into agent responses
    """
    
    def __init__(self):
        self.acknowledgment_templates = self._initialize_acknowledgments()
        self.bridge_templates = self._initialize_bridges()
        
    def _initialize_acknowledgments(self) -> Dict[str, List[str]]:
        """Initialize varied acknowledgment templates"""
        return {
            'concern': [
                "I hear your concern about {topic}.",
                "That's a valid point about {topic}.",
                "I understand why {topic} matters to you.",
                "{topic} is definitely important.",
                "You're right to think about {topic}."
            ],
            'question': [
                "Good question about {topic}.",
                "Let me address {topic}.",
                "About {topic} -",
                "Regarding {topic},",
                "To answer your question about {topic},"
            ],
            'statement': [
                "I appreciate you sharing that.",
                "That's interesting.",
                "Fair point.",
                "I see what you mean.",
                "That makes sense."
            ],
            'objection': [
                "I get it.",
                "I hear you.",
                "Totally understand.",
                "That's fair.",
                "I see where you're coming from."
            ],
            'interest': [
                "Great to hear you're interested in {topic}!",
                "That's exactly the right mindset.",
                "Love that you're thinking about {topic}.",
                "Perfect, {topic} is key here.",
                "Exactly - {topic} is what this is all about."
            ]
        }
        
    def _initialize_bridges(self) -> Dict[str, List[str]]:
        """Initialize bridge phrases to connect acknowledgment to main point"""
        return {
            'pivot': [
                "Speaking of which,",
                "That actually brings me to",
                "Which is why I wanted to ask",
                "That's related to what I was saying -",
                "Along those lines,"
            ],
            'contrast': [
                "At the same time,",
                "That said,",
                "On the flip side,",
                "However,",
                "But here's the thing -"
            ],
            'addition': [
                "And on top of that,",
                "Plus,",
                "Also,",
                "What's more,",
                "And another thing -"
            ],
            'direct': [
                "So, let's talk about",
                "Now, let's move to",
                "Anyway, let's get back to",
                "But let me ask you this -",
                "Quick question though, and then we'll pivot back -"
            ]
        }
        
    def integrate_user_context(self, user_input: str, next_script: str, 
                              integration_style: Optional[IntegrationStyle] = None) -> str:
        """
        Integrate user context into the next response
        
        Args:
            user_input: What the user just said
            next_script: The next scripted line to deliver
            integration_style: Optional specific style to use
            
        Returns:
            Integrated response that sounds natural
        """
        logging.debug(f"ContextIntegrator.integrate_user_context: user_input='{user_input}', next_script='{next_script}', requested_style={integration_style}")
        # Determine integration style if not specified
        if not integration_style:
            integration_style = self._determine_integration_style(user_input)
            logging.debug(f"ContextIntegrator.integrate_user_context: Determined integration_style: {integration_style.value}")
            
        # Apply the appropriate integration
        if integration_style == IntegrationStyle.IGNORE:
            logging.debug("ContextIntegrator.integrate_user_context: Ignoring user context.")
            return next_script
            
        elif integration_style == IntegrationStyle.ACKNOWLEDGE:
            acknowledgment = self._generate_acknowledgment(user_input)
            bridge = self._select_bridge('direct')
            response = f"{acknowledgment} {bridge} {next_script}"
            logging.debug(f"ContextIntegrator.integrate_user_context: Acknowledge style response: '{response}'")
            logging.debug(f"ContextIntegrator.integrate_user_context: Returning response: '{response}'")
            return response
            
        elif integration_style == IntegrationStyle.ANSWER:
            answer = self._generate_answer(user_input)
            bridge = self._select_bridge('pivot')
            response = f"{answer} {bridge} {next_script}"
            logging.debug(f"ContextIntegrator.integrate_user_context: Answer style response: '{response}'")
            logging.debug(f"ContextIntegrator.integrate_user_context: Returning response: '{response}'")
            return response
            
        elif integration_style == IntegrationStyle.WEAVE:
            response = self._weave_context(user_input, next_script)
            logging.debug(f"ContextIntegrator.integrate_user_context: Weave style response: '{response}'")
            logging.debug(f"ContextIntegrator.integrate_user_context: Returning response: '{response}'")
            return response
            
        elif integration_style == IntegrationStyle.BRIDGE:
            bridge_phrase = self._create_contextual_bridge(user_input)
            response = f"{bridge_phrase} {next_script}"
            logging.debug(f"ContextIntegrator.integrate_user_context: Bridge style response: '{response}'")
            logging.debug(f"ContextIntegrator.integrate_user_context: Returning response: '{response}'")
            return response
            
        elif integration_style == IntegrationStyle.EMPATHIZE:
            empathy = self._generate_empathy(user_input)
            response = f"{empathy} {next_script}"
            logging.debug(f"ContextIntegrator.integrate_user_context: Empathize style response: '{response}'")
            logging.debug(f"ContextIntegrator.integrate_user_context: Returning response: '{response}'")
            return response
            
        elif integration_style == IntegrationStyle.REFRAME:
            reframe = self._reframe_statement(user_input)
            response = f"{reframe} {next_script}"
            logging.debug(f"ContextIntegrator.integrate_user_context: Reframe style response: '{response}'")
            logging.debug(f"ContextIntegrator.integrate_user_context: Returning response: '{response}'")
            return response
            
        logging.warning(f"ContextIntegrator.integrate_user_context: Unknown integration style: {integration_style}. Returning original script.")
        logging.debug(f"ContextIntegrator.integrate_user_context: Returning original script (fallback): '{next_script}'")
        return next_script
        
    def _determine_integration_style(self, user_input: str) -> IntegrationStyle:
        """Determine the best integration style based on user input"""
        user_input_lower = user_input.lower()
        logging.debug(f"ContextIntegrator._determine_integration_style: Analyzing user input: '{user_input}'")
        
        # Questions need answers
        if '?' in user_input:
            logging.debug("ContextIntegrator._determine_integration_style: Identified as question. Returning ANSWER.")
            return IntegrationStyle.ANSWER
            
        # Concerns with "but" need acknowledgment
        if any(word in user_input_lower for word in ['but', 'however', 'although']):
            logging.debug("ContextIntegrator._determine_integration_style: Identified as concern. Returning ACKNOWLEDGE.")
            return IntegrationStyle.ACKNOWLEDGE
            
        # Strong objections need empathy
        if any(word in user_input_lower for word in ['busy', 'no time', 'not interested']):
            logging.debug("ContextIntegrator._determine_integration_style: Identified as strong objection. Returning EMPATHIZE.")
            return IntegrationStyle.EMPATHIZE
            
        # Company/trust concerns need weaving
        if any(word in user_input_lower for word in ['company', 'trust', 'legitimate', 'scam']):
            logging.debug("ContextIntegrator._determine_integration_style: Identified as company/trust concern. Returning WEAVE.")
            return IntegrationStyle.WEAVE
            
        # Simple agreements can be ignored or bridged
        if any(word in user_input_lower for word in ['yes', 'yeah', 'okay', 'sure']):
            # Sometimes acknowledge, sometimes just continue
            chosen_style = random.choice([IntegrationStyle.IGNORE, IntegrationStyle.BRIDGE])
            logging.debug(f"ContextIntegrator._determine_integration_style: Identified as simple agreement. Randomly chose: {chosen_style.value}.")
            return chosen_style
            
        # Default to acknowledgment
        logging.debug("ContextIntegrator._determine_integration_style: Defaulting to ACKNOWLEDGE.")
        return IntegrationStyle.ACKNOWLEDGE
        
    def _generate_acknowledgment(self, user_input: str) -> str:
        """Generate a brief acknowledgment"""
        # Simplified and compliant acknowledgment phrases.
        core_acknowledgments = [
            "I understand.",
            "I hear you.",
            "Got it.",
            "That makes sense.",
            "Fair point.",
            "Okay.",
            "No worries.",
            "Understood.",
            "Totally get it.",
            "No rush.",
            "I get it.",
            "Totally fair.",
            "Sure."
        ]
        # Return a simple, compliant acknowledgment.
        return random.choice(core_acknowledgments)
        
    def _generate_answer(self, user_input: str) -> str:
        """Generate a brief answer to a question"""
        user_lower = user_input.lower()
        
        # Common question patterns and answers
        if 'what is this' in user_lower or 'what are you' in user_lower:
            return "This is about building passive income through digital assets."
        elif 'how does' in user_lower or 'how do' in user_lower:
            return "It works by ranking simple websites on Google for local services."
        elif 'why' in user_lower:
            return "Because this is a proven model that's worked for thousands."
        elif 'who are you' in user_lower:
            return "I'm Jake, calling about the opportunity you inquired about."
        elif 'company' in user_lower:
            return "We've been in business for over 10 years helping people build passive income."
        else:
            return "That's a great question."
            
    def _weave_context(self, user_input: str, next_script: str) -> str:
        """Weave user context directly into the script"""
        user_lower = user_input.lower()
        
        # Extract key concern
        if 'company' in user_lower:
            # Weave in company info
            return next_script.replace(
                "do you work for someone",
                "since you're curious about the company - we've been around 10+ years - do you work for someone"
            )
        elif 'trust' in user_lower or 'legitimate' in user_lower:
            # Weave in credibility
            return f"I get the trust concern - we've helped over 7,500 people. {next_script}"
        elif 'busy' in user_lower:
            # Weave in time acknowledgment
            return f"I know you're busy, so I'll be quick - {next_script}"
        else:
            # If the next script is already a complete answer (e.g., from KB), return it as is.
            # Otherwise, use a generic acknowledgment.
            if next_script.strip().endswith('?'): # Heuristic: if it ends with a question, it's likely a complete thought
                return next_script
            else:
                # Rule 3: Echo user's phrasing for generic acknowledgment fallback
                if len(user_input.split()) > 3:
                    return f"Okay, you mentioned {user_input.lower()}. {next_script}"
                else:
                    return f"Fair point. {next_script}"
            
    def _select_bridge(self, bridge_type: str) -> str:
        """Select a bridge phrase"""
        bridges = self.bridge_templates.get(bridge_type, self.bridge_templates['direct'])
        # Ensure bridge phrases don't end with punctuation that would create multiple sentences
        return random.choice(bridges).rstrip('.,;!?')
        
    def _create_contextual_bridge(self, user_input: str) -> str:
        """Create a contextual bridge based on user input"""
        user_lower = user_input.lower()
        
        # Contextual bridges based on what they said
        if 'yes' in user_lower or 'yeah' in user_lower:
            bridges = ["Perfect.", "Great.", "Excellent.", "Good to hear."]
        elif 'maybe' in user_lower or 'possibly' in user_lower:
            bridges = ["I appreciate the honesty.", "Fair enough.", "That's understandable."]
        elif 'no' in user_lower:
            bridges = ["No problem.", "That's okay.", "I understand."]
        else:
            bridges = ["Okay.", "Got it.", "I see.", "Alright."]
            
        return random.choice(bridges)
        
    def _generate_empathy(self, user_input: str) -> str:
        """Generate an empathetic response"""
        user_lower = user_input.lower()
        
        if 'busy' in user_lower:
            empathy_responses = [
                "I totally get that you're busy.",
                "I know time is precious.",
                "I understand you've got a lot going on.",
                "I hear you on being busy."
            ]
        elif 'not interested' in user_lower:
            empathy_responses = [
                "I understand if this isn't for everyone.",
                "That's totally fair.",
                "I get where you're coming from.",
                "No problem, I understand."
            ]
        elif 'skeptical' in user_lower or 'trust' in user_lower:
            empathy_responses = [
                "Skepticism is healthy, I get it.",
                "I understand the concern.",
                "Trust has to be earned, I get that.",
                "That's a smart way to think."
            ]
        else:
            empathy_responses = [
                "I hear you.",
                "I understand.",
                "That makes sense.",
                "I get it."
            ]
            
        return random.choice(empathy_responses)
        
    def _reframe_statement(self, user_input: str) -> str:
        """Reframe the user's statement positively"""
        user_lower = user_input.lower()
        
        if 'busy' in user_lower:
            return "Actually, busy people are exactly who this works best for."
        elif 'no money' in user_lower or 'broke' in user_lower:
            return "That's exactly why building passive income matters."
        elif 'not sure' in user_lower:
            return "Being cautious is smart."
        elif 'complicated' in user_lower:
            return "It's actually simpler than it sounds."
        else:
            return "That's one way to look at it."
            
    def _extract_topic(self, user_input: str) -> str:
        """Extract the main topic from user input"""
        # Simple topic extraction - can be enhanced
        words = user_input.lower().split()
        
        # Look for key topic words
        topic_keywords = ['company', 'money', 'time', 'program', 'business', 'income', 'work']
        
        for word in words:
            if word in topic_keywords:
                return word
                
        # Default to generic
        return "that"
        
    def create_natural_transition(self, previous_topic: str, next_topic: str) -> str:
        """
        Create a natural transition between topics
        
        Args:
            previous_topic: What was just discussed
            next_topic: What we're moving to
            
        Returns:
            Natural transition phrase
        """
        transitions = [
            f"Speaking of {previous_topic}, let me ask you about {next_topic}.",
            f"That's actually related to {next_topic}.",
            f"Which brings me to {next_topic}.",
            f"On a related note, {next_topic}.",
            f"That reminds me to ask about {next_topic}."
        ]
        
        return random.choice(transitions)
        
    def avoid_robotic_patterns(self, response: str) -> str:
        """
        Check and fix robotic patterns in responses
        
        Args:
            response: The generated response
            
        Returns:
            More natural sounding response
        """
        # Remove excessive "I understand" at the beginning
        robotic_starts = [
            "I understand. I understand",
            "I get it. I get it",
            "I hear you. I hear you"
        ]
        
        for pattern in robotic_starts:
            if response.startswith(pattern):
                # Keep only one
                response = response[len(pattern)//2:].strip()
                
        # Remove excessive politeness
        if response.count("please") > 2:
            # Remove some "please"
            response = response.replace("please", "", response.count("please") - 1)
            
        # Fix repeated phrases
        words = response.split()
        cleaned = []
        prev_phrase = ""
        
        for i in range(len(words)):
            current_phrase = " ".join(words[i:min(i+3, len(words))])
            if current_phrase != prev_phrase:
                cleaned.append(words[i])
                prev_phrase = current_phrase
                
        return " ".join(cleaned) if len(cleaned) < len(words) else response