# Objection Handling Syntax & Framework

## 1. Overview

This document outlines the rules, logic, and architecture for the AI phone setter's conversational engine. The primary goal is to create a dynamic, human-like agent that can expertly handle user objections and questions while smoothly guiding the conversation toward its objective.

The system is designed to move beyond robotic scripting and repetition by employing a dynamic, strategy-based approach to conversation management, context integration, and objection handling.

## 2. Core Logic Flow

Each time a user finishes speaking, the AI follows a sophisticated evaluation and response generation process, orchestrated by the `ResponseOrchestrator` in `generative_objection_handler.py`.

1.  **Input Analysis & Transition Evaluation:** The user's response is first analyzed by the `TransitionEvaluator`.
    *   **Goal Met?** It checks if the response satisfies the current node's `transition_conditions`.
    *   **Example:** If the node requires the user to agree to the idea of earning more money, the evaluator looks for expressions of interest or affirmation.

2.  **Decision Point:**
    *   **If Goal is Met:** The AI prepares to transition to the next node. Before doing so, the `ContextIntegrator` checks if the user added any other questions or statements that need addressing. It will generate a brief, natural acknowledgment before moving on to the next node's script.
    *   **If Goal is NOT Met:** This triggers the full objection handling workflow. The system assumes an objection or question is blocking progress and must be resolved.

3.  **Objection/Question Handling:**
    *   **Identify Type:** The system identifies the nature of the objection (e.g., "busy," "skeptical," "no money," "business model question").
    *   **Select Strategy:** The `StrategyTracker` and `DynamicStrategyGenerator` select a persuasive strategy that has **not** been used before for this specific objection (e.g., `SOCIAL_PROOF`, `IMPACT_FOCUS`, `LOGICAL_REASONING`). This is the key to avoiding repetition.
    *   **Integrate Context:** The `ContextIntegrator` ensures the user's specific words are woven into the response, so they feel heard.
    *   **Generate Response:** The system crafts a new response that integrates the user's statement, applies the chosen strategy, and pivots back to the original node's goal with a new question.

4.  **Response Validation:** Before speaking, the final response is validated to ensure it meets critical rules: it's 2-3 sentences, uses simple language, and ends with a question.

## 3. Key Principles & Rules

This framework is governed by a set of core principles to ensure dynamic and effective conversations.

### Rule 1: Goal-Oriented Re-engagement

The AI cannot move to the next node until the current node's objective is met. If an objection is handled but the goal is still not achieved, the AI **must** re-engage.

*   **Bad:** "I understand you're busy. Anyway, do you work for someone or own a business?" (Ignores the unresolved goal).
*   **Good:** "I understand you're busy. That's why this is so powerful - it creates income without trading time. Just hypothetically, what would an extra $20k a month do for you?" (Handles objection and re-engages on the goal with a new angle).

### Rule 2: Dynamic Strategy Selection (No Repetition)

The AI is explicitly forbidden from repeating itself. When re-engaging or handling a recurring objection, it must use a fundamentally different persuasive strategy. Simply changing synonyms is not acceptable.

*   **Initial Strategy (Direct Value):** "Would you be angry with an extra $20k every month?"
*   **User Objection:** "I'm not sure that's realistic."
*   **Second Strategy (Impact Focus):** "I get that it sounds like a big number. But let's just imagine for a second it *was* possible. How would that kind of money impact your life?"
*   **Third Strategy (Social Proof):** "Fair enough. The reason I ask is we have over 7,000 people doing this already, and that's the average they're seeing. Are you generally open to new opportunities?"

### Rule 3: Organic Context Integration

The AI must sound like it's listening by organically incorporating the user's statements into its responses.

*   **User:** "I'd love to make an extra $20k, I could pay my grandmother's medical bills."
*   **Bad (Robotic Acknowledgment):** "I appreciate you sharing that. By the way, do you work for someone right now or do you own your own business?"
*   **Good (Natural Integration):** "That's incredible that you're supporting your family like that. Things like medical bills are exactly why having extra, passive income is a game-changer. To see if this is even a fit, do you currently work for someone or run your own business?"

### Rule 4: Smooth Conversational Flow

Every AI response must be designed to move the conversation forward smoothly.
*   **Concise:** 2-3 short sentences maximum.
*   **Simple Language:** 6th-grade reading level.
*   **End with a Question:** The AI must always end its turn with a question that prompts a useful response and guides the user toward the node's transition condition. Ending on a statement is forbidden as it creates awkward silence.

### Rule 5: Knowledge Base (KB) Integration

When the user asks a specific question about the company, process, or legitimacy, the AI uses the KB.
*   **Synthesize, Don't Recite:** The AI provides a natural, conversational summary of the KB information.
*   **Answer, then Pivot:** It answers the question directly and then immediately pivots back to the script's goal.
*   **Example:** "That's a great question. We've been helping people build these digital assets for over 10 years. And speaking of building, the first step is figuring out your current situation. Do you work for yourself or someone else?"

## 4. System Architecture

This logic is primarily implemented in the following Python modules:

*   `generative_objection_handler.py`: Contains the core `ResponseOrchestrator` and the new, dynamic handling framework.
*   `caller_agent.py`: The main agent that manages state, invokes the handlers, and controls the conversation flow.
*   `conversation_state_manager.py`: Tracks conversation history, personality types, and which strategies have been used.
*   `transition_evaluator.py`: Determines if a node's goal has been met based on the user's response.
*   `prompts.py` & `global_prompt.py`: Define the base-level instructions and persona for the LLM.
