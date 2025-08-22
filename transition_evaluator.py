import logging
from typing import Optional, List, Dict
from livekit.agents import llm

class LLMTransitionEvaluator:
    def __init__(self):
        logging.info("LLMTransitionEvaluator initialized.")

    async def evaluate(self, user_input: str, transitions: List[Dict], llm_instance: llm.LLM) -> Optional[str]:
        """
        Evaluates the user input against the possible transitions for the current node
        using an LLM to determine the most likely transition.
        """
        if not transitions:
            return None

        # Format the transitions for the prompt
        formatted_transitions = "{\n"
        for t in transitions:
            name = t.get("name", "Unknown")
            condition = t.get("condition", "No condition specified.")
            target = t.get("target", "None")
            # Ensure the condition is a clean, single-line string for the prompt
            condition_cleaned = ' '.join(condition.split())
            formatted_transitions += f'  "{target}": "{name}: {condition_cleaned}",\n'
        formatted_transitions += "}"

        prompt = f"""
You are an expert at understanding conversational flow. Your task is to determine the next step in a conversation based on the user's most recent statement.

The user just said: "{user_input}"

Based on this, which of the following transitions should be taken?

Here are the possible transitions and their conditions:
{formatted_transitions}

Analyze the user's statement and choose the single best transition from the list above. Respond with ONLY the target node ID (e.g., "N_IntroduceModel_And_AskQuestions_V3_Adaptive"). If none of the conditions are clearly met, respond with the word "None".
"""
        
        chat = [
            llm.ChatMessage(
                role=llm.ChatRole.SYSTEM,
                content=prompt,
            )
        ]
        
        try:
            # Use a non-streaming call for a single, complete response
            response = await llm_instance.chat(chat)
            response_text = response.choices[0].message.content.strip()

            # Check if the response is a valid target node ID
            valid_targets = [t.get("target") for t in transitions]
            if response_text in valid_targets:
                logging.info(f"LLM chose transition to: {response_text}")
                return response_text
            else:
                logging.info(f"LLM responded with '{response_text}', which is not a valid target or is 'None'. No transition taken.")
                return None

        except Exception as e:
            logging.error(f"Error during LLM call in TransitionEvaluator: {e}")
            return None
