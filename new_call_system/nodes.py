from abc import ABC, abstractmethod
import re
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from new_call_system.engine import ConversationEngine
    from new_call_system.state import ConversationState


class Node(ABC):
    """Abstract base class for all nodes in the conversation flow."""
    def __init__(self, engine: 'ConversationEngine', state: 'ConversationState'):
        self.engine = engine
        self.state = state
        self.node_id = self.__class__.__name__

    @abstractmethod
    async def enter_node(self):
        pass

    @abstractmethod
    async def handle_response(self, user_input: str) -> Optional[str]:
        pass

    async def speak(self, text: str):
        await self.engine.speak(text)

# --- TERMINAL & SHARED NODES ---

class N_EndCall_Final_V2_Decisive(Node):
    async def enter_node(self):
        await self.speak("Okay, perfect. You are all set then, {{customer_name}}. Have a great rest of your day. Goodbye.")
        if self.engine.agent_session:
            await self.engine.agent_session.close()
    async def handle_response(self, user_input: str) -> Optional[str]:
        return None

class N_IntroduceModel_And_AskQuestions_V3_Adaptive(Node):
    async def enter_node(self):
        await self.speak("Okay. In a nutshell, we set up passive income websites, and we let them produce income for you.")
        await self.speak("What questions come to mind as soon as you hear something like that?")
    async def handle_response(self, user_input: str) -> Optional[str]:
        return "N_KB_Q&A_With_StrategicNarrative_V3_Adaptive"

# --- OPENER NODES ---

class N001A_NameConfirmation_Only(Node):
    async def enter_node(self):
        await self.speak("{{customer_name}}?")
    async def handle_response(self, user_input: str) -> Optional[str]:
        wrong_number_keywords = ["wrong number", "not him", "not her", "not speaking"]
        if any(keyword in user_input.lower() for keyword in wrong_number_keywords):
            return "N_EndCall_Final_V2_Decisive"
        return "N001B_IntroAndHelpRequest_Only"

class N001B_IntroAndHelpRequest_Only(Node):
    async def enter_node(self):
        await self.speak("This is Jake. I was just, um, wondering if you could possibly help me out for a moment?")
    async def handle_response(self, user_input: str) -> Optional[str]:
        return "N_Opener_StackingIncomeHook_V3_CreativeTactic"

class N_Opener_StackingIncomeHook_V3_CreativeTactic(Node):
    async def enter_node(self):
        await self.speak("Well, uh I don't know if you could yet, but, I'm calling because you filled out an ad about stacking income without stacking hours.")
        await self.speak("I know this call is out of the blue, but do you have just 25 seconds for me to explain why I'm reaching out today specifically?")

    async def handle_response(self, user_input: str) -> Optional[str]:
        user_input_lower = user_input.lower()

        not_interested_keywords = ["not interested", "no thanks", "not for me"]
        if any(keyword in user_input_lower for keyword in not_interested_keywords):
            return "N_Obj_EarlyDismiss_AskShareBackground_V7"

        no_time_keywords = ["no time", "busy", "call me back", "another time"]
        if any(keyword in user_input_lower for keyword in no_time_keywords):
            return "N_Obj_RealBusy_BluntCheck_V3_Adaptive"

        no_recall_keywords = ["don't remember", "don't recall", "what ad", "when was this"]
        if any(keyword in user_input_lower for keyword in no_recall_keywords):
            return "N003_NoRecall_PivotAndChallenge_V18_FullyTuned"

        permission_keywords = ["yes", "sure", "okay", "what is it", "explain", "curious"]
        if any(keyword in user_input_lower for keyword in permission_keywords):
            return "N_IntroduceModel_And_AskQuestions_V3_Adaptive"

        return "N003B_DeframeInitialObjection_V7_GoalOriented"

# --- OBJECTION HANDLING & EARLY INTEREST NODES ---

class N_Obj_EarlyDismiss_AskShareBackground_V7(Node):
    async def enter_node(self):
        await self.speak("I understand the skepticism. I was skeptical too until I became a student myself. And I’m not just any student. Do you mind if I take 20 seconds to share a bit about my background?")
    async def handle_response(self, user_input: str) -> Optional[str]:
        # Simplified logic for now
        if "no" in user_input.lower():
            return "N_Obj_EarlyDismiss_DirectValueChallenge_V9_EscalationEnabled"
        return "N_Obj_EarlyDismiss_ShareBackground_DeliverStoryHook_V3_FullyTuned"

class N_Obj_RealBusy_BluntCheck_V3_Adaptive(Node):
    async def enter_node(self):
        await self.speak("Let me be blunt. Are you not sure why you should be listening to this, or is there a meeting coming up for you right now?")
    async def handle_response(self, user_input: str) -> Optional[str]:
        # Placeholder logic
        return "N_EndCall_Final_V2_Decisive" # Placeholder

class N003_NoRecall_PivotAndChallenge_V18_FullyTuned(Node):
    async def enter_node(self):
        await self.speak("Gotcha, Are you focused on creating new income streams right now?")
    async def handle_response(self, user_input: str) -> Optional[str]:
        if "yes" in user_input.lower():
            return "N_IntroduceModel_And_AskQuestions_V3_Adaptive"
        # Add more complex logic from the prompt later
        await self.speak("Okay. So just to be clear, is finding new ways to increase your income simply not a priority for you right now?")
        return None # Stay in node

class N003B_DeframeInitialObjection_V7_GoalOriented(Node):
    async def enter_node(self):
        # This node is dynamic. For now, we'll use a generic de-framing question.
        await self.speak("When you say that, is it because you've seen things like this before, or is it just a bad time?")
    async def handle_response(self, user_input: str) -> Optional[str]:
        # Simplified transition
        return "N_IntroduceModel_And_AskQuestions_V3_Adaptive"
