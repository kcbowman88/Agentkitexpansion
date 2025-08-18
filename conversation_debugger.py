"""
Conversation flow debugger and analyzer.
Provides detailed logging and analysis tools for troubleshooting conversation issues.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import os


# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('conversation_debug.log'),
        logging.StreamHandler()
    ]
)


@dataclass
class ConversationEvent:
    """Represents a single event in the conversation flow."""
    timestamp: str
    event_type: str  # 'user_input', 'objection_detected', 'strategy_selected', 'response_generated', 'transition'
    node_id: str
    details: Dict[str, Any]
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class ConversationDebugger:
    """
    Debugger for analyzing conversation flows and identifying issues.
    """
    
    def __init__(self, session_id: str = None):
        """
        Initialize the conversation debugger.
        
        Args:
            session_id: Unique identifier for this conversation session
        """
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger = logging.getLogger(f"ConversationDebugger_{self.session_id}")
        self.events: List[ConversationEvent] = []
        self.issues_detected: List[Dict[str, Any]] = []
        
        # Create debug output directory
        self.debug_dir = f"debug_sessions/{self.session_id}"
        os.makedirs(self.debug_dir, exist_ok=True)
        
        self.logger.info(f"Conversation debugger initialized for session: {self.session_id}")
    
    def log_user_input(self, node_id: str, user_input: str, context: Dict[str, Any] = None):
        """
        Log user input event.
        
        Args:
            node_id: Current node ID
            user_input: The user's input text
            context: Additional context information
        """
        event = ConversationEvent(
            timestamp=datetime.now().isoformat(),
            event_type="user_input",
            node_id=node_id,
            details={
                "user_input": user_input,
                "context": context or {}
            }
        )
        self.events.append(event)
        self.logger.debug(f"USER INPUT at {node_id}: {user_input}")
        
        # Check for potential issues
        self._check_user_input_issues(user_input, node_id)
    
    def log_objection_detected(self, node_id: str, objection_type: str, 
                               user_input: str, confidence: float = 1.0):
        """
        Log objection detection event.
        
        Args:
            node_id: Current node ID
            objection_type: Type of objection detected
            user_input: The user's input that triggered objection
            confidence: Confidence score of objection detection
        """
        event = ConversationEvent(
            timestamp=datetime.now().isoformat(),
            event_type="objection_detected",
            node_id=node_id,
            details={
                "objection_type": objection_type,
                "user_input": user_input,
                "confidence": confidence
            }
        )
        self.events.append(event)
        self.logger.info(f"OBJECTION DETECTED at {node_id}: {objection_type} (confidence: {confidence})")
    
    def log_strategy_selected(self, node_id: str, strategy: str, 
                             used_strategies: List[str], reason: str = ""):
        """
        Log strategy selection event.
        
        Args:
            node_id: Current node ID
            strategy: Selected strategy
            used_strategies: List of previously used strategies
            reason: Reason for selecting this strategy
        """
        event = ConversationEvent(
            timestamp=datetime.now().isoformat(),
            event_type="strategy_selected",
            node_id=node_id,
            details={
                "strategy": strategy,
                "used_strategies": used_strategies,
                "reason": reason
            }
        )
        self.events.append(event)
        self.logger.info(f"STRATEGY SELECTED at {node_id}: {strategy} (previously used: {used_strategies})")
        
        # Check for strategy repetition issues
        self._check_strategy_issues(strategy, used_strategies, node_id)
    
    def log_response_generated(self, node_id: str, response: str, 
                              strategy: str = None, integration_style: str = None):
        """
        Log response generation event.
        
        Args:
            node_id: Current node ID
            response: Generated response text
            strategy: Strategy used for generation
            integration_style: Context integration style used
        """
        event = ConversationEvent(
            timestamp=datetime.now().isoformat(),
            event_type="response_generated",
            node_id=node_id,
            details={
                "response": response,
                "strategy": strategy,
                "integration_style": integration_style,
                "response_length": len(response),
                "ends_with_question": response.strip().endswith("?")
            }
        )
        self.events.append(event)
        self.logger.info(f"RESPONSE GENERATED at {node_id}: {response[:100]}...")
        
        # Check for response quality issues
        self._check_response_issues(response, node_id)
    
    def log_transition(self, from_node: str, to_node: str, 
                       transition_key: str, reason: str = ""):
        """
        Log node transition event.
        
        Args:
            from_node: Source node ID
            to_node: Destination node ID
            transition_key: Transition key used
            reason: Reason for transition
        """
        event = ConversationEvent(
            timestamp=datetime.now().isoformat(),
            event_type="transition",
            node_id=from_node,
            details={
                "from_node": from_node,
                "to_node": to_node,
                "transition_key": transition_key,
                "reason": reason
            }
        )
        self.events.append(event)
        self.logger.info(f"TRANSITION: {from_node} -> {to_node} via {transition_key}")
    
    def log_error(self, node_id: str, error_type: str, 
                  error_message: str, context: Dict[str, Any] = None):
        """
        Log error event.
        
        Args:
            node_id: Current node ID where error occurred
            error_type: Type of error
            error_message: Error message
            context: Additional error context
        """
        event = ConversationEvent(
            timestamp=datetime.now().isoformat(),
            event_type="error",
            node_id=node_id,
            details={
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {}
            }
        )
        self.events.append(event)
        self.logger.error(f"ERROR at {node_id}: {error_type} - {error_message}")
        
        # Record as issue
        self.issues_detected.append({
            "timestamp": datetime.now().isoformat(),
            "node_id": node_id,
            "issue_type": "error",
            "details": {
                "error_type": error_type,
                "error_message": error_message
            }
        })
    
    def _check_user_input_issues(self, user_input: str, node_id: str):
        """Check for potential issues in user input."""
        # Check for very short responses that might be ambiguous
        if len(user_input.strip()) < 3:
            self._record_issue(node_id, "ambiguous_input", 
                             f"Very short user input: '{user_input}'")
        
        # Check for potential misunderstandings
        confusion_indicators = ["what?", "huh?", "i don't understand", "confused"]
        if any(indicator in user_input.lower() for indicator in confusion_indicators):
            self._record_issue(node_id, "user_confusion", 
                             f"User seems confused: '{user_input}'")
    
    def _check_strategy_issues(self, strategy: str, used_strategies: List[str], node_id: str):
        """Check for strategy selection issues."""
        # Check for repetition
        if strategy in used_strategies:
            self._record_issue(node_id, "strategy_repetition", 
                             f"Strategy '{strategy}' has been used before")
        
        # Check for too many strategies used
        if len(used_strategies) > 5:
            self._record_issue(node_id, "excessive_strategies", 
                             f"Too many strategies used ({len(used_strategies)})")
    
    def _check_response_issues(self, response: str, node_id: str):
        """Check for response quality issues."""
        # Check for robotic patterns
        sentences = response.split('.')
        if len(sentences) == 4 and all(len(s.strip()) < 20 for s in sentences if s.strip()):
            self._record_issue(node_id, "robotic_pattern", 
                             "Response has robotic 4-sentence pattern")
        
        # Check for missing question
        if not response.strip().endswith("?"):
            self._record_issue(node_id, "missing_question", 
                             "Response doesn't end with a question")
        
        # Check for repetitive phrases
        repetitive_phrases = ["let me", "i understand", "that's"]
        phrase_count = sum(1 for phrase in repetitive_phrases 
                          if response.lower().count(phrase) > 1)
        if phrase_count > 2:
            self._record_issue(node_id, "repetitive_phrases", 
                             "Response contains repetitive phrases")
        
        # Check for overly long response
        if len(response) > 500:
            self._record_issue(node_id, "response_too_long", 
                             f"Response is too long ({len(response)} chars)")
    
    def _record_issue(self, node_id: str, issue_type: str, details: str):
        """Record a detected issue."""
        issue = {
            "timestamp": datetime.now().isoformat(),
            "node_id": node_id,
            "issue_type": issue_type,
            "details": details
        }
        self.issues_detected.append(issue)
        self.logger.warning(f"ISSUE DETECTED at {node_id}: {issue_type} - {details}")
    
    def analyze_conversation_flow(self) -> Dict[str, Any]:
        """
        Analyze the entire conversation flow and generate insights.
        
        Returns:
            Dictionary containing analysis results
        """
        analysis = {
            "session_id": self.session_id,
            "total_events": len(self.events),
            "total_issues": len(self.issues_detected),
            "event_breakdown": {},
            "strategy_usage": {},
            "node_visits": {},
            "objection_types": {},
            "average_response_length": 0,
            "issues_by_type": {},
            "conversation_loops": []
        }
        
        # Count events by type
        for event in self.events:
            event_type = event.event_type
            analysis["event_breakdown"][event_type] = \
                analysis["event_breakdown"].get(event_type, 0) + 1
            
            # Track node visits
            node_id = event.node_id
            analysis["node_visits"][node_id] = \
                analysis["node_visits"].get(node_id, 0) + 1
            
            # Track strategy usage
            if event.event_type == "strategy_selected":
                strategy = event.details.get("strategy")
                if strategy:
                    analysis["strategy_usage"][strategy] = \
                        analysis["strategy_usage"].get(strategy, 0) + 1
            
            # Track objection types
            if event.event_type == "objection_detected":
                obj_type = event.details.get("objection_type")
                if obj_type:
                    analysis["objection_types"][obj_type] = \
                        analysis["objection_types"].get(obj_type, 0) + 1
            
            # Calculate average response length
            if event.event_type == "response_generated":
                response_length = event.details.get("response_length", 0)
                if analysis["average_response_length"] == 0:
                    analysis["average_response_length"] = response_length
                else:
                    analysis["average_response_length"] = \
                        (analysis["average_response_length"] + response_length) / 2
        
        # Count issues by type
        for issue in self.issues_detected:
            issue_type = issue["issue_type"]
            analysis["issues_by_type"][issue_type] = \
                analysis["issues_by_type"].get(issue_type, 0) + 1
        
        # Detect conversation loops (node visited more than 3 times)
        for node_id, visits in analysis["node_visits"].items():
            if visits > 3:
                analysis["conversation_loops"].append({
                    "node_id": node_id,
                    "visits": visits
                })
        
        return analysis
    
    def generate_report(self, include_recommendations: bool = True) -> str:
        """
        Generate a human-readable report of the conversation analysis.
        
        Args:
            include_recommendations: Whether to include recommendations
            
        Returns:
            Formatted report string
        """
        analysis = self.analyze_conversation_flow()
        
        report = []
        report.append("=" * 80)
        report.append(f"CONVERSATION ANALYSIS REPORT")
        report.append(f"Session ID: {self.session_id}")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Events: {analysis['total_events']}")
        report.append(f"Total Issues: {analysis['total_issues']}")
        report.append(f"Average Response Length: {analysis['average_response_length']:.0f} chars")
        report.append("")
        
        # Event Breakdown
        report.append("EVENT BREAKDOWN")
        report.append("-" * 40)
        for event_type, count in analysis['event_breakdown'].items():
            report.append(f"  {event_type}: {count}")
        report.append("")
        
        # Strategy Usage
        if analysis['strategy_usage']:
            report.append("STRATEGY USAGE")
            report.append("-" * 40)
            for strategy, count in sorted(analysis['strategy_usage'].items(), 
                                         key=lambda x: x[1], reverse=True):
                report.append(f"  {strategy}: {count} times")
            report.append("")
        
        # Objection Types
        if analysis['objection_types']:
            report.append("OBJECTION TYPES ENCOUNTERED")
            report.append("-" * 40)
            for obj_type, count in sorted(analysis['objection_types'].items(), 
                                         key=lambda x: x[1], reverse=True):
                report.append(f"  {obj_type}: {count} times")
            report.append("")
        
        # Issues Detected
        if analysis['issues_by_type']:
            report.append("ISSUES DETECTED")
            report.append("-" * 40)
            for issue_type, count in sorted(analysis['issues_by_type'].items(), 
                                           key=lambda x: x[1], reverse=True):
                report.append(f"  {issue_type}: {count} occurrences")
            report.append("")
        
        # Conversation Loops
        if analysis['conversation_loops']:
            report.append("CONVERSATION LOOPS DETECTED")
            report.append("-" * 40)
            for loop in analysis['conversation_loops']:
                report.append(f"  Node {loop['node_id']}: visited {loop['visits']} times")
            report.append("")
        
        # Recommendations
        if include_recommendations:
            recommendations = self._generate_recommendations(analysis)
            if recommendations:
                report.append("RECOMMENDATIONS")
                report.append("-" * 40)
                for i, rec in enumerate(recommendations, 1):
                    report.append(f"  {i}. {rec}")
                report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Check for excessive issues
        if analysis['total_issues'] > 5:
            recommendations.append("High number of issues detected. Review conversation flow logic.")
        
        # Check for strategy repetition
        if 'strategy_repetition' in analysis['issues_by_type']:
            recommendations.append("Strategy repetition detected. Ensure strategy tracker is working correctly.")
        
        # Check for conversation loops
        if analysis['conversation_loops']:
            recommendations.append("Conversation loops detected. Review transition conditions and goal achievement logic.")
        
        # Check for robotic patterns
        if 'robotic_pattern' in analysis['issues_by_type']:
            recommendations.append("Robotic response patterns detected. Improve response variation and naturalness.")
        
        # Check for missing questions
        if 'missing_question' in analysis['issues_by_type']:
            recommendations.append("Some responses missing questions. Ensure all objection responses end with engaging questions.")
        
        # Check response length
        if analysis['average_response_length'] > 400:
            recommendations.append("Responses may be too long. Consider more concise messaging.")
        elif analysis['average_response_length'] < 100:
            recommendations.append("Responses may be too short. Ensure adequate value communication.")
        
        return recommendations
    
    def save_session(self):
        """Save the debug session to files."""
        # Save events
        events_file = os.path.join(self.debug_dir, "events.json")
        with open(events_file, 'w') as f:
            json.dump([event.to_dict() for event in self.events], f, indent=2)
        
        # Save issues
        issues_file = os.path.join(self.debug_dir, "issues.json")
        with open(issues_file, 'w') as f:
            json.dump(self.issues_detected, f, indent=2)
        
        # Save analysis
        analysis_file = os.path.join(self.debug_dir, "analysis.json")
        with open(analysis_file, 'w') as f:
            json.dump(self.analyze_conversation_flow(), f, indent=2)
        
        # Save report
        report_file = os.path.join(self.debug_dir, "report.txt")
        with open(report_file, 'w') as f:
            f.write(self.generate_report())
        
        self.logger.info(f"Debug session saved to {self.debug_dir}")


# Global debugger instance for easy access
_global_debugger: Optional[ConversationDebugger] = None


def get_debugger(session_id: str = None) -> ConversationDebugger:
    """
    Get or create a global debugger instance.
    
    Args:
        session_id: Optional session ID for new debugger
        
    Returns:
        ConversationDebugger instance
    """
    global _global_debugger
    if _global_debugger is None or session_id:
        _global_debugger = ConversationDebugger(session_id)
    return _global_debugger


def debug_conversation_flow(func):
    """
    Decorator to automatically debug conversation flow methods.
    
    Usage:
        @debug_conversation_flow
        def handle_objection(self, user_input, node_id):
            ...
    """
    def wrapper(*args, **kwargs):
        debugger = get_debugger()
        
        # Log method entry
        debugger.logger.debug(f"Entering {func.__name__} with args: {args[1:]} kwargs: {kwargs}")
        
        try:
            result = func(*args, **kwargs)
            debugger.logger.debug(f"Exiting {func.__name__} with result: {result}")
            return result
        except Exception as e:
            debugger.log_error(
                node_id=kwargs.get('node_id', 'unknown'),
                error_type=type(e).__name__,
                error_message=str(e)
            )
            raise
    
    return wrapper