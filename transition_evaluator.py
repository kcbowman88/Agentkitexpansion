import logging
from typing import Optional, List, Dict
from livekit.agents import llm
import json

class IntentAndTransitionEvaluator:
    def __init__(self):
        logging.info("IntentAndTransitionEvaluator initialized.")

    async def evaluate(self, user_input: str, transitions: List[Dict], llm_instance: llm.LLM) -> Dict:
        """
        Analyzes the user's input to identify both a potential transition and other intents
        like questions or objections. Returns a dictionary of intents.
        """
        if not transitions:
            return {}

        # Format the transitions for the prompt
        formatted_transitions = "{\n"
        for t in transitions:
            name = t.get("name", "Unknown")
            condition = t.get("condition", "No condition specified.")
            target = t.get("target", "None")
            condition_cleaned = ' '.join(condition.split())
            formatted_transitions += f'  "{target}": "{name}: {condition_cleaned}",\n'
        formatted_transitions += "}"

        prompt = f"""
You are an expert at understanding conversational nuance. Your task is to analyze a user's statement and break it down into its core intents.

The user just said: "{user_input}"

1.  **Transition Intent:** Does the user's statement match one of the following transition conditions? If yes, identify the target node ID. If no clear match, use "None".
    {formatted_transitions}

2.  **Question Intent:** Did the user ask a specific question? If so, what is the question? If not, use "None".

3.  **Objection Intent:** Did the user raise an objection or express a concern? If so, what is the objection? If not, use "None".

Please provide your analysis in a JSON object with the following keys: "transition_target", "question", "objection".

Example for "Yeah, that sounds good, but how much does it cost?":
{{
  "transition_target": "N_SomeNode_Positive",
  "question": "how much does it cost?",
  "objection": "None"
}}

Example for "I'm not sure, it sounds a bit complicated.":
{{
  "transition_target": "None",
  "question": "None",
  "objection": "it sounds a bit complicated"
}}

Now, analyze the user's statement and provide the JSON response.
User statement: "{user_input}"
"""
        
        chat = [llm.ChatMessage(role=llm.ChatRole.SYSTEM, content=prompt)]
        
        try:
            response = await llm_instance.chat(chat)
            response_text = response.choices[0].message.content.strip()

            # Clean the response to ensure it's valid JSON
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            intents = json.loads(response_text)
            logging.info(f"LLM identified intents: {intents}")
            return intents

        except Exception as e:
            logging.error(f"Error during LLM call or JSON parsing in IntentAndTransitionEvaluator: {e}")
            # Return a default object that won't cause a crash
            return {"transition_target": None, "question": None, "objection": None}
