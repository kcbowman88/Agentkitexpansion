import warnings
warnings.warn("This module is deprecated and will be removed in a future version. Please use 'generative_objection_handler' instead.", DeprecationWarning)

# gdp_phrases.py

GDP_PHRASE_BANKS = {
    "S": {
        "IntroduceModel": {
            "acknowledgment": [
                "No rush, I hear you.",
                "I understand, no pressure at all.",
                "Totally fair, I get it.",
                "I hear your hesitation, no worries.",
                "Understood, I'm not here to push.",
                "Okay, I'm listening, take your time."
            ],
            "micro_moves": [
                "Got it.",
                "Understood.",
                "Okay.",
                "Right.",
                "I see.",
                "Fair enough."
            ],
            "general_disinterest": { # User says "Not really."
                "objection_handle": [
                    "Sounds like you're feeling a bit unsure about this right now.",
                    "It seems like you're not quite seeing the immediate value, and that's okay.",
                    "Many folks feel a bit hesitant at first, and that's perfectly normal.",
                    "I get that this might not seem relevant right off the bat.",
                    "It's common to feel a little disengaged at this stage.",
                    "I appreciate your honesty about not being fully interested."
                ],
                "pivot": [
                    "Would it be impossible to just hear the one quick idea, so you can decide if it's even worth your time?",
                    "We can keep this super quick and just share the one simple idea. Would you be open to hearing that now?",
                    "To make sure I'm not wasting your time, would you be comfortable with just hearing the one-liner to see if it aligns?",
                    "Could we take just a moment for me to share the core concept, so you can quickly assess if it's for you?",
                    "Would you be against me briefly explaining the main point, just to give you a clearer picture?",
                    "Is it okay if I share the one key takeaway, so you have all the info to make a decision?"
                ]
            },
            "time_busy": { # User says "I'm super busy," "Call me back."
                "objection_handle": [
                    "Sounds like you're feeling super busy right now, and your time is valuable.",
                    "I hear you, it's a busy day, and I appreciate you even picking up.",
                    "I understand you've got a lot on your plate, and I respect that.",
                    "It seems like time is really tight for you right now.",
                    "I get that you're swamped, and I don't want to add to that.",
                    "Understood, you're in the middle of something important."
                ],
                "pivot": [
                    "Would it be impossible to just hear the one quick idea now, so you don't have to wait for a call back?",
                    "We can keep this super quick and just share the one simple idea. Would you be open to hearing that now?",
                    "To make sure I'm not wasting your time, would you be comfortable with just hearing the one-liner to see if it aligns?",
                    "Could we take just a moment for me to share the core concept, so you can quickly assess if it's for you?",
                    "Would you be against me briefly explaining the main point, just to give you a clearer picture?",
                    "Is it okay if I share the one key takeaway, so you have all the info to make a decision?"
                ]
            },
            # Add other intent_categories as needed for IntroduceModel
        },
        "N_Opener_StackingIncomeHook_V3_CreativeTactic": {
            "acknowledgment": [
                "No rush, I hear you.",
                "I understand, no pressure at all.",
                "Totally fair, I get it.",
                "I hear your hesitation, no worries.",
                "Understood, I'm not here to push.",
                "Okay, I'm listening, take your time."
            ],
            "micro_moves": [
                "Got it.",
                "Understood.",
                "Okay.",
                "Right.",
                "I see.",
                "Fair enough."
            ],
            "general_disinterest": { # User says "Not really."
                "objection_handle": [
                    "Sounds like you're feeling a bit unsure about this right now.",
                    "It seems like you're not quite seeing the immediate value, and that's okay.",
                    "Many folks feel a bit hesitant at first, and that's perfectly normal.",
                    "I get that this might not seem relevant right off the bat.",
                    "It's common to feel a little disengaged at this stage.",
                    "I appreciate your honesty about not being fully interested."
                ],
                "pivot": [
                    "Would it be impossible to just hear the one quick idea, so you can decide if it's even worth your time?",
                    "We can keep this super quick and just share the one simple idea. Would you be open to hearing that now?",
                    "To make sure I'm not wasting your time, would you be comfortable with just hearing the one-liner to see if it aligns?",
                    "Could we take just a moment for me to share the core concept, so you can quickly assess if it's for you?",
                    "Would you be against me briefly explaining the main point, just to give you a clearer picture?",
                    "Is it okay if I share the one key takeaway, so you have all the info to make a decision?"
                ]
            },
            "time_busy": { # User says "I'm super busy," "Call me back."
                "objection_handle": [
                    "Sounds like you're feeling super busy right now, and your time is valuable.",
                    "I hear you, it's a busy day, and I appreciate you even picking up.",
                    "I understand you've got a lot on your plate, and I respect that.",
                    "It seems like time is really tight for you right now.",
                    "I get that you're swamped, and I don't want to add to that.",
                    "Understood, you're in the middle of something important."
                ],
                "pivot": [
                    "Would it be impossible to just hear the one quick idea now, so you don't have to wait for a call back?",
                    "We can keep this super quick and just share the one simple idea. Would you be open to hearing that now?",
                    "To make sure I'm not wasting your time, would you be comfortable with just hearing the one-liner to see if it aligns?",
                    "Could we take just a moment for me to share the core concept, so you can quickly assess if it's for you?",
                    "Would you be against me briefly explaining the main point, just to give you a clearer picture?",
                    "Is it okay if I share the one key takeaway, so you have all the info to make a decision?"
                ]
            },
        }
        # Add other personas (D, I, C) and their nodes/intent_categories as needed
    }
}

NODE_GOALS_AND_CRITERIA = {
    "IntroduceModel": {
        "goal": "Introduce the core concept (passive income websites) and keep momentum.",
        "transition_criteria": "user provides a consent-like signal or a short affirmative to proceed."
    }
    # Add other nodes as needed
}