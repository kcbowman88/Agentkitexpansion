# Complete Conversation Script

This document provides a comprehensive overview of the conversation flow, including all scripts and transitions for each node in the system. It details the architecture of the unified `CallFlowAgent` and its integrated components, reflecting the dynamic and adaptive nature of the conversation.

## 0. Agent Architecture Overview

The agent is built around a single, unified `CallFlowAgent` that dynamically adapts its behavior based on the conversation state, user input, and a sophisticated objection handling system.

### Core Components:
- **`CallFlowAgent` (`caller_agent.py`):** The central orchestrator of the conversation. It manages the `CallFlowState`, processes user input, determines transitions between conversation nodes, and integrates with specialized modules for advanced functionalities.
- **`CallFlowState` (defined in `caller_agent.py`):** A dataclass that maintains the entire state of the conversation, including customer information, current node, personality type, emotional state, objection history, conversation context, user preferences, qualification status, and more. This state is continuously updated and used to personalize the agent's responses.
- **`AgentSession` (configured in [`agent.py`](agent.py)):** Manages the low-level audio and communication aspects, including Speech-to-Text (STT) via Deepgram, Text-to-Speech (TTS) via ElevenLabs (with OpenAI fallback), and Voice Activity Detection (VAD) for turn management. It passes the `CallFlowState` as user data to the `CallFlowAgent`.
    - **Manual Turn Detection (RPC Methods):** When `TURN_DETECTION_MODE` is set to "manual", the `AgentSession` registers RPC methods (`start_turn`, `end_turn`, `cancel_turn`) to allow external control over the agent's listening state, enabling precise turn management from a frontend.
- **`Global Prompt` (`global_prompt.py`):** Defines the agent's core identity (Jake), persona, universal rules of engagement, and high-level call flow strategy. It provides the foundational instructions for the agent's behavior.
- **`ObjectionHandler` (`objection_handler.py`):** A sophisticated, multi-phase engine that detects, categorizes, and responds to user objections. It uses persona-specific response banks, dynamic pivots, and A/B testing flags to adapt its strategies. It ensures the conversation remains goal-oriented even when facing resistance.
- **`DISCClassifier` (integrated in `caller_agent.py`):** Analyzes user input to classify their DISC personality type (Dominant, Influential, Steady, Conscientious), which then informs persona-specific adaptations in responses and transitions.
- **`TacticalResponder` (integrated in `caller_agent.py`):** Provides concise, strategic responses for ambiguous or unhandled user inputs, helping to keep the conversation on track.
- **`KBProcessor` (integrated in `caller_agent.py`):** Queries a knowledge base to provide relevant information and dynamically generate responses, especially for Q&A nodes.

### Dynamic Behavior and Adaptations:
The agent's responses and transitions are highly dynamic, influenced by:
- **User Input Analysis:** [`_analyze_sentiment()`](caller_agent.py:281), personality classification (via `DISCClassifier`), and keyword detection are used to understand user intent and emotional state.
- **Conversation History:** The agent maintains a detailed history of exchanges, which is summarized by [`_summarize_conversation_context()`](caller_agent.py:164) and used to inform context-aware responses.
- **Qualification Status:** The agent tracks the user's engagement, understanding, goal alignment, and financial readiness using [`_update_qualification_status()`](caller_agent.py:203), adapting the conversation flow accordingly.
- **Objection Handling:** Objections trigger a specialized system (the `ObjectionHandler`) that uses persona-specific strategies, response rotation, and mandatory pivots to re-anchor the conversation to its goals.
- **Dynamic Script Generation:** For certain nodes (e.g., KB Q&A), scripts are generated on-the-fly using [`_generate_dynamic_kb_qa_script()`](caller_agent.py:1583), incorporating personalized data, dynamic income figures, and adaptive questioning.
- **Fallback Mechanisms:** Robust fallback transitions, implemented in [`_fallback_transition()`](caller_agent.py:85), ensure the conversation can recover gracefully from unexpected inputs or unhandled scenarios.

## 1. Opening & Triage

### N001A_NameConfirmation_Only
**Goal:** Say the person's name with a question mark. Nothing else.

**Context:** This is the AI's VERY FIRST utterance after the call connects and the prospect has likely said "Hello?" or similar. Only say their name, nothing else. If you don't have a name in the variable default to saying - John?

**Script:** `{{customer_name}}?`

**Transitions:**
- default → N001B_IntroAndHelpRequest_Only

### N001B_IntroAndHelpRequest_Only
**Goal:** Ask them if they could help you out.

**Context:** Entered immediately after N001A_NameConfirmation_Only once the prospect has responded to their name being called.

**Script:** "This is Jake. I was just, um, wondering if you could possibly help me out for a moment?"

**Transitions:**
- default → N_Opener_StackingIncomeHook_V3_CreativeTactic

### N_Opener_StackingIncomeHook_V3_CreativeTactic
**Goal:** To introduce the agent and context, deliver the "stacking income without stacking hours" hook, and get the user's permission to explain further.

**Context:** This is an early-call node used to set the frame immediately after the user has confirmed their name.

**Script:** "Well, uh I don't know if you could yet, but, I'm calling because you filled out an ad about stacking income without stacking hours. I know this call is out of the blue, but do you have just 25 seconds for me to explain why I'm reaching out today specifically?"

**Transitions:**
- permission_granted → N_IntroduceModel_And_AskQuestions_V3_Adaptive
- no_recall → N003_NoRecall_PivotAndChallenge_V18_FullyTuned
- objection_or_callback_request → N003B_DeframeInitialObjection_V7_GoalOriented
- not_interested → N_Obj_EarlyDismiss_AskShareBackground_V7
- no_time → N_Obj_RealBusy_BluntCheck_V3_Adaptive
- question → N_KB_Q&A_With_StrategicNarrative_V3_Adaptive
- default → N_IntroduceModel_And_AskQuestions_V3_Adaptive
- personality_D → N_IntroduceModel_And_AskQuestions_V3_Adaptive_Dominant
- personality_I → N_IntroduceModel_And_AskQuestions_V3_Adaptive_Influential
- personality_S → N_IntroduceModel_And_AskQuestions_V3_Adaptive_Steady
- personality_C → N_IntroduceModel_And_AskQuestions_V3_Adaptive_Conscientious
- context_high_engagement → N_IntroduceModel_And_AskQuestions_V3_Adaptive_HighEngagement
- context_low_engagement → N_Obj_EarlyDismiss_AskShareBackground_V7

## 2. Main Path - Explanation & Qualification

### N_IntroduceModel_And_AskQuestions_V3_Adaptive
**Goal:** To deliver a concise, high-level summary of the business model and then proactively ask an open-ended question to surface the user's initial thoughts or concerns.

**Context:** You are entering this node after the user has shown initial interest and is ready for a basic explanation of what the program does.

**Script:** "Okay. In a nutshell, we set up passive income websites, and we let them produce income for you. What questions come to mind as soon as you hear something like that?"

**Transitions:**
- default → N_KB_Q&A_With_StrategicNarrative_V3_Adaptive

### N_IntroduceModel_And_AskQuestions_V3_Adaptive Variants

#### N_IntroduceModel_And_AskQuestions_V3_Adaptive_Dominant
**Goal:** To deliver a concise, high-level summary of the business model and then proactively ask an open-ended question to surface the user's initial thoughts or concerns (Dominant personality variant).

**Context:** You are entering this node after the user has shown initial interest and is ready for a basic explanation of what the program does. The user has been classified as having a Dominant personality type.

**Script:** "Okay. In a nutshell, we set up passive income websites that generate revenue with minimal ongoing effort. What's the biggest concern you have about this model?"

#### N_IntroduceModel_And_AskQuestions_V3_Adaptive_Influential
**Goal:** To deliver a concise, high-level summary of the business model and then proactively ask an open-ended question to surface the user's initial thoughts or concerns (Influential personality variant).

**Context:** You are entering this node after the user has shown initial interest and is ready for a basic explanation of what the program does. The user has been classified as having an Influential personality type.

**Script:** "Okay. In a nutshell, we set up passive income websites, and we let them produce income for you. Isn't that exciting? What aspects of this do you find most interesting?"

#### N_IntroduceModel_And_AskQuestions_V3_Adaptive_Steady
**Goal:** To deliver a concise, high-level summary of the business model and then proactively ask an open-ended question to surface the user's initial thoughts or concerns (Steady personality variant).

**Context:** You are entering this node after the user has shown initial interest and is ready for a basic explanation of what the program does. The user has been classified as having a Steady personality type.

**Script:** "Okay. In a nutshell, we set up passive income websites, and we let them produce income for you. Take your time to think about it. What questions come to mind as you consider this opportunity?"

#### N_IntroduceModel_And_AskQuestions_V3_Adaptive_Conscientious
**Goal:** To deliver a concise, high-level summary of the business model and then proactively ask an open-ended question to surface the user's initial thoughts or concerns (Conscientious personality variant).

**Context:** You are entering this node after the user has shown initial interest and is ready for a basic explanation of what the program does. The user has been classified as having a Conscientious personality type.

**Script:** "Okay. In a nutshell, we set up passive income websites, and we let them produce income for you. I can provide more detailed information about the process if you'd like. What specific aspects would you like to know more about?"

#### N_IntroduceModel_And_AskQuestions_V3_Adaptive_HighEngagement
**Goal:** To deliver a concise, high-level summary of the business model and then proactively ask an open-ended question to surface the user's initial thoughts or concerns (High engagement variant).

**Context:** You are entering this node after the user has shown high engagement and interest. They've asked questions or made positive comments.

**Script:** "Great! I can tell you're really engaged with this. In a nutshell, we set up passive income websites, and we let them produce income for you. Since you seem interested, what specific aspects would you like to know more about?"

### N_KB_Q&A_With_StrategicNarrative_V3_Adaptive
**Goal:** To dynamically answer the user's questions using the `qualifier setter` KB, ensure the core income potential has been discussed, and then deliver the "$20k" value-framing question.

**Context:** You are entering this node after the user has acknowledged the "Rank and Bank" concept and is asking questions.

**Implementation:** This is a FULLY DYNAMIC implementation that generates personalized responses rather than using a fixed script. The actual response is generated based on user data and conversation context to make the conversation feel more natural and human-like. The dynamic script is generated using the [`_generate_dynamic_kb_qa_script()`](caller_agent.py:1583) method in the [`caller_agent.py`](caller_agent.py) file. This method leverages the [`KBProcessor`](kb_processor.py) to query the knowledge base and the [`ObjectionHandler.enforce_pivot()`](objection_handler.py:1581) to ensure the response is goal-oriented.

**Personalization Variables:**
The dynamic implementation uses the following personalization variables to tailor the conversation:
- `{{customer_name}}` - The user's name
- `{{previous_questions}}` - Questions the user has asked in the conversation
- `{{expressed_interests}}` - Topics or aspects the user has shown interest in
- `{{employment_status}}` - Whether the user is employed, self-employed, or unemployed
- `{{income_level}}` - The user's current income or revenue
- `{{personality_type}}` - DISC personality classification (D, I, S, C)
- `{{engagement_level}}` - How engaged the user has been in the conversation (0-10 scale)
- `{{specific_concerns}}` - Concerns or objections the user has raised

**How Personalization Variables Are Used:**
- `{{customer_name}}` is used to address the user directly, making the conversation more personal.
- `{{previous_questions}}` are used to reference the user's specific inquiries and provide relevant answers.
- `{{expressed_interests}}` help tailor the response to topics the user cares about.
- `{{employment_status}}` influences how income potential is framed (supplemental for employed, additional streams for business owners, recovery for unemployed).
- `{{income_level}}` is used to calculate dynamic income figures that are relevant to the user's financial situation.
- `{{personality_type}}` affects the tone and structure of the response (direct for D, enthusiastic for I, supportive for S, analytical for C).
- `{{engagement_level}}` determines the level of detail in the response (concise for low engagement, detailed for high engagement).
- `{{specific_concerns}}` are addressed directly to provide reassurance and build trust.

**Dynamic Income Figures:**
Instead of hardcoded figures, income references are dynamically calculated based on the user's financial situation:
- For Employed Users: Building on their current income, showing potential for supplemental income (40% to 120% of current income)
- For Business Owners: Referencing their stated monthly revenue, showing potential for additional income streams (20% to 200% of current revenue)
- For Unemployed Users: Referencing their past income, showing potential for recovery and growth (30% to 150% of past income)

When income data is not available, a generic income statement is used that focuses on the potential of the opportunity without specific figures.

The income range is calculated as a percentage of the user's current/past financial situation, adjusted by their engagement level (0.8x to 1.2x multiplier).

**How Dynamic Income Figures Are Calculated:**
The `_calculate_dynamic_income_range` method in `caller_agent.py` takes the user's income level, employment status, and engagement level to calculate a personalized income range. The calculation considers:
- Base percentage ranges for each employment status
- Engagement level multiplier to adjust the range
- Rounding to the nearest thousand for readability

**Adaptive Questioning:**
The closing question is dynamically selected based on:
- Previous questions asked by the user
- Expressed interests and concerns
- Employment status
- Personality type
- Engagement level

**How Adaptive Questioning Changes Based on User's Previous Responses:**
- If the user asked technical questions, the closing question focuses on technical aspects vs. financial potential
- If the user asked about timeline, the question references realistic timeframes for results
- If the user asked about risk, the question addresses risk management for their profile
- If the user asked about time commitment, the question discusses time requirements for their situation
- For high engagement users, the question is more detailed and specific
- For medium engagement users, the question is balanced in detail
- For low engagement users, the question is concise and direct

**Script Structure Variants:**
Different script structures are used based on:
- DISC personality classification (Dominant, Influential, Steady, Conscientious)
- Engagement level (High, Medium, Low)

**How Script Variations Work for Different Personality Types and Engagement Levels:**
- Dominant (D): Direct and results-focused, emphasizing potential income and quick results
- Influential (I): Enthusiastic and engaging, emphasizing success stories and possibilities
- Steady (S): Supportive and methodical, emphasizing stability and proven processes
- Conscientious (C): Detailed and analytical, emphasizing data and processes
- High Engagement: More detailed and in-depth, referencing specific previous comments
- Medium Engagement: Balanced detail and brevity, general references to interests
- Low Engagement: Concise and direct, focusing on core value proposition

**User Data Integration:**
The dynamic node integrates with conversation history, employment and income information (when available), DISC personality classification, engagement metrics, and time constraints to provide a personalized experience. When income information is not available, the node uses a generic approach to discuss income potential.

**How User Data Is Integrated for Better Tailoring:**
- Conversation history is used to maintain context and reference previous exchanges
- Employment and income information is used to calculate relevant income figures
- DISC personality classification is used to adjust tone and approach
- Engagement metrics influence the level of detail and interaction style
- Time constraints (if mentioned) are considered in the response

**Implementation Notes:**
The dynamic script generation process uses the [`_generate_dynamic_kb_qa_script()`](caller_agent.py:1583) method in [`caller_agent.py`](caller_agent.py), which:
1. Retrieves user data for personalization (name, personality type, engagement level, interests, employment status, income level) from the `CallFlowState`.
2. Queries the knowledge base using [`self.kb_processor.query()`](kb_processor.py) based on user interests and conversation history.
3. Calculates dynamic income figures using [`_calculate_dynamic_income_range()`](caller_agent.py:1672) based on the user's financial situation.
4. Generates a personalized opening using [`_get_personality_based_opening()`](caller_agent.py:1713) based on personality type.
5. Creates an income potential statement with dynamic figures using [`_generate_income_statement()`](caller_agent.py:1746).
6. Generates an adaptive closing question using [`_generate_adaptive_question()`](caller_agent.py:1789) based on the user's previous responses.
7. Combines all parts into the final script, and then applies the mandatory pivot using [`ObjectionHandler.enforce_pivot()`](objection_handler.py:1581).

**Dynamic Question Answering:**
The node dynamically answers user questions by:
1. Using the [`_query_knowledge_base()`](caller_agent.py:1866) method (which in turn calls `KBProcessor.query()`) to find relevant information based on user interests and conversation history.
2. Generating natural language responses that directly address the user's questions.
3. Incorporating personalization variables to make the answers more relevant.

**Core Income Potential Discussion:**
The implementation ensures core income potential has been discussed by:
1. Including dynamic income figures in the response when income data is available, or using a generic income statement when it's not
2. Referencing relevant success stories based on user profile
3. Providing realistic expectations based on user's financial situation when available
4. Connecting income potential to user's specific profile when possible

**Value-Framing Question:**
The "$20k" value-framing question is delivered by:
1. Presenting income potential in user-relevant terms through dynamic income figures
2. Framing the value proposition around the user's specific situation
3. Using adaptive questioning that leads to value recognition
4. Maintaining the core concept while personalizing the presentation
 
**Transitions:**
- default → N200_Super_WorkAndIncomeBackground_V3_Adaptive

### N200_Super_WorkAndIncomeBackground_V3_Adaptive
**Goal:** To leverage a positive interaction with an upbeat tone and determine the user's employment status (employee vs. owner).

**Context:** You are entering this node after a positive or humorous interaction with {{customer_name}}.

**Script:** "Alright, love that! So, are you working for someone right now or do you run your own business?"

**Transitions:**
- employed → N201A_Employed_AskYearlyIncome_V8_Adaptive
- business_owner → N202A_AskCurrentMonthlyRevenue_V7_FullyTuned
- unemployed → N201E_Unemployed_EmpathyAskPastYearlyIncome_V5_Adaptive
- default → N201A_Employed_AskYearlyIncome_V8_Adaptive
- personality_D → N200_Super_WorkAndIncomeBackground_V3_Adaptive_Dominant
- personality_I → N200_Super_WorkAndIncomeBackground_V3_Adaptive_Influential
- personality_S → N200_Super_WorkAndIncomeBackground_V3_Adaptive_Steady
- personality_C → N200_Super_WorkAndIncomeBackground_V3_Adaptive_Conscientious

### N200_Super_WorkAndIncomeBackground_V3_Adaptive Variants

#### N200_Super_WorkAndIncomeBackground_V3_Adaptive_Dominant
**Goal:** To leverage a positive interaction with an upbeat tone and determine the user's employment status (employee vs. owner) (Dominant personality variant).

**Context:** You are entering this node after a positive or humorous interaction with {{customer_name}}. The user has been classified as having a Dominant personality type.

**Script:** "Great! So, are you currently employed or running your own business? I'm looking to understand your current situation so we can determine how this opportunity fits."

#### N200_Super_WorkAndIncomeBackground_V3_Adaptive_Influential
**Goal:** To leverage a positive interaction with an upbeat tone and determine the user's employment status (employee vs. owner) (Influential personality variant).

**Context:** You are entering this node after a positive or humorous interaction with {{customer_name}}. The user has been classified as having an Influential personality type.

**Script:** "That's fantastic! So, are you working for someone right now or do you run your own business? I'd love to hear about your current situation!"

#### N200_Super_WorkAndIncomeBackground_V3_Adaptive_Steady
**Goal:** To leverage a positive interaction with an upbeat tone and determine the user's employment status (employee vs. owner) (Steady personality variant).

**Context:** You are entering this node after a positive or humorous interaction with {{customer_name}}. The user has been classified as having a Steady personality type.

**Script:** "I'm glad you're enjoying this! So, are you working for someone right now or do you run your own business? Take your time to think about it."

#### N200_Super_WorkAndIncomeBackground_V3_Adaptive_Conscientious
**Goal:** To leverage a positive interaction with an upbeat tone and determine the user's employment status (employee vs. owner) (Conscientious personality variant).

**Context:** You are entering this node after a positive or humorous interaction with {{customer_name}}. The user has been classified as having a Conscientious personality type.

**Script:** "That's wonderful! So, are you working for someone right now or do you run your own business? I'm interested in understanding your current professional situation."

## 3. Income & Vehicle Questions

### N201A_Employed_AskYearlyIncome_V8_Adaptive
**Goal:** To efficiently and professionally ask {{customer_name}} for their approximate current yearly income.

**Context:** You are entering this node after {{customer_name}} has confirmed they are currently employed.

**Script:** "Got it. And what's that job producing for you yearly, approximately?"

**Transitions:**
- default → N201B_Employed_AskSideHustle_V4_FullyTuned

### N201B_Employed_AskSideHustle_V4_FullyTuned
**Goal:** To smoothly and efficiently ask {{customer_name}} if they have had any side hustles or other income sources in the last two years.

**Context:** You are entering this node after {{customer_name}} (an employed prospect) has shared their current yearly income.

**Script:** "And in the last two years, did you happen to have any kind of side hustle or anything else bringing in income?"

**Transitions:**
- yes → N201C_Employed_AskSideHustleAmount_V3_FullyTuned
- no → N201D_Employed_AskVehicleQ_V5_Adaptive
- default → N201D_Employed_AskVehicleQ_V5_Adaptive

### N201C_Employed_AskSideHustleAmount_V3_FullyTuned
**Goal:** To positively acknowledge the user's side hustle and then efficiently ask for the approximate monthly income it generated.

**Context:** You are entering this node after {{customer_name}} (an employed prospect) has confirmed they have or had a side hustle.

**Script:** "Okay, great. And what was that side hustle bringing in for you, say, on a good month?"

**Transitions:**
- default → N201D_Employed_AskVehicleQ_V5_Adaptive

### N201D_Employed_AskVehicleQ_V5_Adaptive
**Goal:** To ask {{customer_name}} the 'Vehicle Question' with a confident, solution-oriented tone, gauging if they can envision this model as a way to generate income comparable to or exceeding their current earnings.

**Context:** You are entering this node after discussing the current income of an employed user.

**Script:** "Got it. So, do you see yourself being able to generate at least that same kind of amount you're making, say {Amount_Reference_Employed}, or even more, using a vehicle like this digital real estate model if you had the right system and support?"

**Transitions:**
- affirms_vehicle → Logic_Split_Node_Financial_Qualification
- default → Logic_Split_Node_Financial_Qualification

### N202A_AskCurrentMonthlyRevenue_V7_FullyTuned
**Goal:** To directly and professionally ask {{customer_name}}, a business owner, for their approximate current monthly revenue.

**Context:** You are entering this node after {{customer_name}} has identified as a business owner.

**Script:** "Okay. As a business owner, where's your monthly revenue at right now, roughly?"

**Transitions:**
- default → N202B_AskHighestRevenueMonth_V4_FullyTuned

### N202B_AskHighestRevenueMonth_V4_FullyTuned
**Goal:** To acknowledge the user's current monthly revenue and then directly ask for their business's highest monthly revenue point achieved within the last two years.

**Context:** You are entering this node after {{customer_name}}, a business owner, has provided their current monthly revenue.

**Script:** "And in the last two years, what was the highest monthly revenue point your business hit?"

**Transitions:**
- default → N202C_AskVehicleQuestion_BusinessOwner_V4_Adaptive

### N202C_AskVehicleQuestion_BusinessOwner_V4_Adaptive
**Goal:** To ask {{customer_name}} the 'Vehicle Question' with a confident, solution-oriented tone, gauging if they can envision this model as a way to generate significant clear profit.

**Context:** You are entering this node after discussing the revenue of a business owner.

**Script:** "So, thinking about the kind of numbers your business has achieved, do you see yourself being able to generate at least {Amount_Reference_Phrase}, or perhaps even more, using a vehicle like this rank and bank model if it was structured correctly for you?"

**Transitions:**
- affirms_vehicle → Logic_Split_Node_Financial_Qualification
- default → Logic_Split_Node_Financial_Qualification

### N201E_Unemployed_EmpathyAskPastYearlyIncome_V5_Adaptive
**Goal:** To first acknowledge {{customer_name}}'s unemployment status with genuine empathy, and then to politely and efficiently ask for their approximate past yearly income.

**Context:** You are entering this node because {{customer_name}} has indicated they are currently unemployed or were recently laid off.

**Script:** "Okay, I'm genuinely sorry to hear that. When you were working, what was that job producing for you yearly, roughly?"

**Transitions:**
- default → N201F_Unemployed_AskSideHustle_V4_FullyTuned

### N201F_Unemployed_AskSideHustle_V4_FullyTuned
**Goal:** To efficiently and conversationally ask {{customer_name}} if they had any side hustles or other income sources in the last two years.

**Context:** You are entering this node after {{customer_name}} has shared their past yearly income.

**Script:** "In the last two years, did you happen to have any kind of side hustle or anything else bringing in income?"

**Transitions:**
- yes → N201G_Unemployed_AskSideHustleAmount
- no → N201H_Unemployed_AskVehicleQ_V4_FullyTuned
- default → N201H_Unemployed_AskVehicleQ_V4_FullyTuned

### N201G_Unemployed_AskSideHustleAmount
**Goal:** To efficiently ask the unemployed user, {{customer_name}}, for the approximate monthly income from their previously mentioned side hustle.

**Context:** You are entering this node after {{customer_name}} has confirmed that they have or had a side hustle.

**Script:** "Okay, great. And what does that side hustle bring in for you monthly, roughly?"

**Transitions:**
- default → N201H_Unemployed_AskVehicleQ_V4_FullyTuned

### N201H_Unemployed_AskVehicleQ_V4_FullyTuned
**Goal:** To ask {{customer_name}} the 'Vehicle Question' with an empathetic, solution-oriented tone, gauging if they can envision this model as a way to generate income comparable to or exceeding their past earnings.

**Context:** You are entering this node after discussing the past income of an unemployed user.

**Script:** "So, do you see yourself being able to generate at least [Amount_Reference_Unemployed], or even more, using a vehicle like this digital real estate model if you had the right system and support to get back on your feet and beyond?"

**Transitions:**
- affirms_vehicle → Logic_Split_Node_Financial_Qualification
- default → Logic_Split_Node_Financial_Qualification

## 4. Financial Qualification

### Logic_Split_Node_Financial_Qualification
**Goal:** Logical branch to route users based on income level.

**Context:** Entered after the user has affirmed they can see themselves generating income using the digital real estate model.

**Script:** ""

**Transitions:**
- high_income → N_AskCapital_15k_V1_Adaptive
- standard_income → N_AskCapital_5k_Direct_V1_Adaptive

### N_AskCapital_15k_V1_Adaptive
**Goal:** To ask the user if they have $15-25k in liquid capital.

**Context:** You are entering this node to begin the direct financial qualification process.

**Script:** "Okay, got it. For this kind of business, it definitely helps to have about fifteen to twenty-five thousand dollars in liquid capital set aside for initial expenses. Is that what you'd generally have on hand, moneywise?"

**Transitions:**
- has_15_25k → N_ConfirmCommitment_FinalCheck_V1_Adaptive
- no_15_25k → N_AskCapital_5k_V1_Adaptive
- default → N_AskCapital_5k_V1_Adaptive

### N_AskCapital_5k_V1_Adaptive
**Goal:** To ask the user if they have the absolute minimum of $5k in liquid capital.

**Context:** You are entering this node because the user has just said 'no' to the $15-25k capital range.

**Script:** "Okay, no problem at all, that's just the typical range. The absolute minimum to get started is closer to five thousand. Would that be more in line for you?"

**Transitions:**
- has_5k → N_ConfirmCommitment_FinalCheck_V1_Adaptive
- no_5k → N205C_AskCreditScore_650_V1_FullyTuned
- default → N205C_AskCreditScore_650_V1_FullyTuned

### N_AskCapital_5k_Direct_V1_Adaptive
**Goal:** To directly ask the user if they have the minimum required liquid capital of five thousand dollars.

**Context:** You are entering this node to begin the financial qualification, starting directly with the minimum capital requirement.

**Script:** "Okay, got it. Now, for the initial expenses to get a business like this started, the absolute minimum is around five thousand dollars. Is that something you'd have access to?"

**Transitions:**
- has_5k → N_ConfirmCommitment_FinalCheck_V1_Adaptive
- no_5k → N205C_AskCreditScore_650_V1_FullyTuned
- default → N205C_AskCreditScore_650_V1_FullyTuned

### N205C_AskCreditScore_650_V1_FullyTuned
**Goal:** To pivot from the lack of liquid capital and professionally ask {{customer_name}} if they have a credit score of at least 650.

**Context:** You are entering this node because the user has indicated they do not have the minimum required liquid capital.

**Script:** "Okay, thanks for being upfront with me. The other way people qualify is with their credit. Do you have a credit score of at least six fifty?"

**Transitions:**
- score_over_650 → N_ConfirmCommitment_FinalCheck_V1_Adaptive
- score_under_650 → Disqualified
- default → Disqualified

### Disqualified
**Goal:** Handle disqualified prospects gracefully

**Context:** The prospect has been disqualified based on financial criteria.

**Script:** "I understand this opportunity might not be the right fit for you at this time. Thank you for your time, and I wish you the best of luck with your endeavors."

**Transitions:**
- default → N_EndCall_Final_V2_Decisive

## 5. Motivation & Scheduling Proposal

### N_ConfirmCommitment_FinalCheck_V1_Adaptive
**Goal:** To get the user to verbally confirm their commitment to the scheduled appointment time.

**Script:** "Aside from emergencies, Is there any reason why you won't be available at that time?"

**Transitions:**
- committed → N401_AskWhyNow_Initial_V10_AssertiveFrame
- default → N401_AskWhyNow_Initial_V10_AssertiveFrame

### N401_AskWhyNow_Initial_V10_AssertiveFrame
**Goal:** To ask the 'Why now?' question and then use assertive, frame-controlling tactics to handle any deferrals or vague responses.

**Context:** You are entering this node because the user is financially qualified.

**Script:** "Okay. Just to understand a bit better, is there a specific reason you're looking to make a change or explore something like this *right now*, as opposed to say, six months from now?"

**Transitions:**
- motivation_provided → N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned
- callback_requested → N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned
- default → N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned
 
### N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned
**Goal:** To sincerely acknowledge the user's reason for their interest, deliver a genuine compliment, and then immediately ask the engaging hook question 'You know why?'.

**Context:** You are entering this node after {{customer_name}} has responded to the 'Why now?' question.

**Script:** "Okay, I appreciate you sharing that. I have to say, that's actually refreshing to hear. You know why?"

**Transitions:**
- callback_requested → N403_IdentityAffirmation_And_ValueFitQuestion_V8_GoalAligned
- default → N403_IdentityAffirmation_And_ValueFitQuestion_V8_GoalAligned

### N403_IdentityAffirmation_And_ValueFitQuestion_V8_GoalAligned
**Goal:** To deliver a sincere identity affirmation and then get the user to confirm that the overall concept resonates with what they are looking for.

**Context:** You are entering this node after the user has engaged with the 'You know why?' hook from the previous node.

**Script:** "Well, let me tell you. I sometimes talk to people that clearly will never give themselves permission to go after their dreams. But you're the type of person that is serious and ready to get started, and I commend you for that. So, does this sound like something that could fit what you're after?"

**Transitions:**
- fits → N500A_ProposeDeeperDive_V5_Adaptive
- callback_requested → N_Obj_RealBusy_BluntCheck_V3_Adaptive
- default → N500A_ProposeDeeperDive_V5_Adaptive

### N500A_ProposeDeeperDive_V5_Adaptive
**Goal:** To confidently affirm that we can help {{customer_name}}, propose scheduling a deeper dive call as the clear next step, and then secure their agreement.

**Context:** You are entering this node after a positive interaction where the user has shown readiness.

**Script:** "Okay, that's excellent. I definitely feel like we can help you with that. What we need to do is set up another call that'll be a deeper dive into your situation. Sound good?"

**Transitions:**
- agrees → N500B_AskTimezone_V2_FullyTuned
- default → N500B_AskTimezone_V2_FullyTuned

### N500B_AskTimezone_V2_FullyTuned
**Goal:** To positively acknowledge the user's agreement to schedule a call and then efficiently and conversationally ask for their timezone.

**Context:** You are entering this node after {{customer_name}} has agreed to schedule the deeper dive call.

**Script:** "Gotcha. And just so I've got it right for our scheduling, what timezone are you in?"

**Transitions:**
- default → N_AskForCallbackRange_V1_Adaptive

### N_AskForCallbackRange_V1_Adaptive
**Goal:** To determine a time range when the user is available at their desk and focused for a callback.

**Script:** "Okay. And when are you typically back at your desk during the day. What's a good time range for you?"

**Transitions:**
- default → N_Scheduling_AskTime_V2_SmartAmbiguity

### N_Scheduling_AskTime_V2_SmartAmbiguity
**Goal:** To ask for a preferred appointment time and intelligently handle AM/PM ambiguity.

**Script:** "Okay, great! And when would be a good time for us to schedule that call?"

**Transitions:**
- default → N_ConfirmVideoCallEnvironment_V1_Adaptive

### N_ConfirmVideoCallEnvironment_V1_Adaptive
**Goal:** To confirm that the user will be able to join the Zoom video call from their computer at the scheduled time.

**Script:** "Okay, great. And just to confirm, the meeting is via Zoom, so does that time work for you to join the video call from your computer?"

**Transitions:**
- confirmed → N206_AskAboutPartners_IfFinanciallyQualified
- default → N206_AskAboutPartners_IfFinanciallyQualified

## 6. Scheduling Logistics

### N206_AskAboutPartners_IfFinanciallyQualified
**Goal:** Ask the final initial qualification question about whether any other decision-makers would be involved.

**Script:** "I don't think I asked, but um is there anyone else that'd be involved in your business, like a spouse or other business partners?"

**Transitions:**
- partner → N018_ConfirmPartnerAvailability
- no_partner → N_ConfirmCommitment_FinalCheck_V1_Adaptive
- default → N_ConfirmCommitment_FinalCheck_V1_Adaptive

### N018_ConfirmPartnerAvailability
**Goal:** Determine if there are partners involved in this.

**Context:** Entered after the prospect has agreed to a specific time slot and a partner is known to exist.

**Script:** "Ok cool. So can {{partner_reference}} 100% be on the call at {{chosen_time_with_ampm}} on {{chosen_day}}?"

**Transitions:**
- available → N_ConfirmCommitment_FinalCheck_V1_Adaptive
- not_available → N_Scheduling_RescheduleAndHandle_V5_FullyTuned
- unsure → N017D_SuggestPartnerCheck_ScheduleFollowUpCall
- default → N_ConfirmCommitment_FinalCheck_V1_Adaptive

### N017D_SuggestPartnerCheck_ScheduleFollowUpCall
**Goal:** When a prospect is unsure of their partner's availability, ask when they can find out, and then propose a brief follow-up call.

**Context:** Entered because the prospect stated they don't know the other decision-maker's schedule.

**Script Part 1:** "[Acknowledge uncertainty]. When's the soonest you can get in touch with them to find out if that time works?"

**Script Part 2:** "[Acknowledge timeframe]. So here's what we're gonna do then. I want you to talk to your [partner] and find out what time will work for the both of you. Then around [suggested follow-up time] I'll give you a quick ring and we'll lock in an official time on the calendar. Sound fair?"

**Transitions:**
- default → N_ConfirmCommitment_FinalCheck_V1_Adaptive

### N_Scheduling_RescheduleAndHandle_V5_FullyTuned
**Goal:** To successfully reschedule the appointment by flexibly using a toolkit of objection handlers.

**Context:** You are entering this node after a webhook has informed you that the user's requested time is unavailable.

**Transitions:**
- new_time_found → N_ConfirmCommitment_FinalCheck_V1_Adaptive
- default → N_ConfirmCommitment_FinalCheck_V1_Adaptive

## 7. Final Confirmation & Close

### N_AskAboutReminderSetup_V1_Adaptive
**Goal:** To ask the user if they know how to set a reminder on their phone.

**Script:** "Okay, great. When you see that text message, it's going to ask you to set up a reminder. Do you know how to set up a reminder on your phone?"

**Transitions:**
- default → N_CheckForTextReceipt_V1_Adaptive

### N_CheckForTextReceipt_V1_Adaptive
**Goal:** To confirm the user has successfully received the confirmation text message.

**Script:** "Okay, that text should be on its way to you now. Did that come through on your end yet?"

**Transitions:**
- received → N_ConfirmAndRequestReply_V4_PatientListener
- default → N_ConfirmAndRequestReply_V4_PatientListener

### N_ConfirmAndRequestReply_V4_PatientListener
**Goal:** To get the user to reply to the confirmation text with the specific phrase, 'Confirmed, I'll see you there,' right now.

**Script:** "Great. Go ahead and respond to that message with the words, Confirmed, I'll see you there. I'll wait for you to do that now."

**Transitions:**
- default → N_Video_Assign_GentleIntro_V3_FullyTuned

### N_Video_Assign_GentleIntro_V3_FullyTuned
**Goal:** To clearly introduce the 12-minute overview video, explain its benefit, and secure the user's agreement to watch it.

**Script Step 1:** "Gotcha, {customer_name}, you're all set. Just one quick thing before your call that Kendrick likes everyone to do. There's a short 12-minute video that's just a good overview, so you've got the basics down and can really dive deep with him. Make sense?"

**Script Step 2:** "Great. So if I send that over when we hang up, are you able to give that a quick watch then?"

**Transitions:**
- agrees → N_Video_ReinforceValue_FeeContext_V3_FullyTuned
- default → N_Video_ReinforceValue_FeeContext_V3_FullyTuned

### N_Video_ReinforceValue_FeeContext_V3_FullyTuned
**Goal:** To reinforce the importance of the pre-call video by clearly stating the value of Kendrick's time and confirming the fee is waived.

**Script:** "Perfect. Yeah, it really helps make that next call super valuable. Kendrick's time is usually set at a thousand dollars for these strategy sessions, but since you'll have seen the overview, that fee is completely waived for you. All good on that front?"

**Transitions:**
- default → N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint
- default → N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint

### N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint
**Goal:** To provide the clear, logical reason why the 12-minute video is essential.

**Script:** "And because we're talking about that kind of scale, that 12-minute video just makes sure you're fully in the loop before you and Kendrick discuss your specific situation, you know?"

**Transitions:**
- logic_acknowledged → N_Video_AssignAndCommit_V1_FullyTuned
- default → N_Video_AssignAndCommit_V1_FullyTuned

### N_Video_AssignAndCommit_V1_FullyTuned
**Goal:** To secure a direct commitment from {{customer_name}} to watch the overview video immediately after the call.

**Script:** "Okay, great. So if I send you that video right after we hang up, are you able to give it a quick watch now?"

**Transitions:**
- commits → N_Video_ConfirmAndReply_V1_Adaptive
- default → N_Video_ConfirmAndReply_V1_Adaptive

### N_Video_ConfirmAndReply_V1_Adaptive
**Goal:** To get the user to reply to the confirmation text with the word 'Got it' right now.

**Script:** "Okay, perfect. Matter of fact, I'm sending that link to your phone right now. Could you do me a favor and just reply 'Got it' so I know you received the link?"

**Transitions:**
- default → N_Finalize_And_EndCall_V1_Adaptive

### N_Finalize_And_EndCall_V1_Adaptive
**Goal:** To deliver the final, critical instruction about replying to the text to avoid cancellation, and then to professionally and warmly end the call.

**Script:** "Alright, you're all set then. The last and most important step is just to reply to that text. If you don't, our system will automatically cancel the appointment to open up the slot. So please make sure you get that done. Have a great day, and take care."

**Transitions:**
- default → N_EndCall_Final_V2_Decisive

### N_EndCall_Final_V2_Decisive
**Goal:** To deliver a final, professional closing statement and then terminate the call.

**Script:** "Okay, perfect. You are all set then, {{customer_name}}. I've just sent that confirmation email over to you. Have a great rest of your day. Goodbye."

**Transitions:**
- default → EndCall

## 8. Dismissal & Busy Loops

### N003B_DeframeInitialObjection_V7_GoalOriented
**Goal:** To skillfully de-frame the user's initial objection in order to elicit a statement of curiosity or interest, opening a path to discuss the passive income opportunity.

**Context:** You are entering this node because the user has just stated an objection after the ad recall question.

**Script:** "I understand. Many people feel that way at first. But let me ask you this - what if it were possible to generate income without the usual headaches?"

**Transitions:**
- default → N_IntroduceModel_And_AskQuestions_V3_Adaptive

### N003_NoRecall_PivotAndChallenge_V18_FullyTuned
**Goal:** To pivot from the user's 'no recall' of the ad, immediately test their interest in the core financial benefit, and directly challenge any initial disinterest to uncover their true priorities.

**Context:** You are entering this node because the user did not remember filling out the ad (e.g., 'Not really,' 'No').

**Script:** "Gotcha, are you focused on creating new income streams right now?"

**Script No:** "Okay. So just to be clear, is finding new ways to increase your income simply not a priority for you *right now*?"

**Transitions:**
- callback_requested → N_Obj_RealBusy_BluntCheck_V3_Adaptive
- shows_interest → N_IntroduceModel_And_AskQuestions_V3_Adaptive
- default → N_IntroduceModel_And_AskQuestions_V3_Adaptive

### N_Obj_EarlyDismiss_AskShareBackground_V7
**Goal:** My primary goal for this turn is to acknowledge {{customer_name}}'s skepticism or early dismissal with understanding, pique their interest with a personal hook ('And I'm not just any student...'), and then politely request just 20 seconds to share a bit of my background, aiming to get their permission ('yes' or equivalent) to proceed.

**Context:** The prospect, {{customer_name}}, has just indicated it's not a good time, they're busy, or shown initial disinterest/skepticism.

**Script:** "No rush, I hear you. Let's get back to the next step."

**Transitions:**
- agrees → N_Obj_EarlyDismiss_ShareBackground_DeliverStoryHook_V3_FullyTuned
- declines → N_Obj_EarlyDismiss_DirectValueChallenge_V9_EscalationEnabled
- default → N_Obj_EarlyDismiss_ShareBackground_DeliverStoryHook_V3_FullyTuned

### N_Obj_EarlyDismiss_ShareBackground_DeliverStoryHook_V3_FullyTuned
**Goal:** To share my relevant personal background to build credibility, state the significant income potential I've witnessed to create intrigue, and then ask an engaging hook question.

**Context:** You are entering this node because {{customer_name}} has just agreed to hear your background.

**Script:** "Great. I'm a military veteran and I have a software engineering degree, so trust me I get how much nonsense is out there. But after actually going through this program myself, I've seen firsthand it's possible for people to pull in an extra 20,000 a month, sometimes even more. Any idea what makes that possible?"

**Transitions:**
- default → N_Obj_EarlyDismiss_ShareBackgroundAskWhy

### N_Obj_EarlyDismiss_ShareBackgroundAskWhy
**Goal:** Share personal background story and ask them if they know why the opportunity is so good.

**Context:** Entered from N_Obj_EarlyDismiss_AskShareBackground after prospect agreed to hear the background.

**Script:** "I am a military veteran. I have a software engineering degree, and I know there's a lot of BS out there. But because I went through the program myself, I can tell you this has given people like me a real shot at an extra 20,000 or more per month. Do you know why?"

**Transitions:**
- default → N_Obj_EarlyDismiss_ExplainReasonAndExplore

### N_Obj_EarlyDismiss_ExplainReasonAndExplore
**Goal:** Edify Product Value, and ask them if it's interesting.

**Context:** Entered from N_Obj_EarlyDismiss_ShareBackgroundAskWhy after prospect responded to 'Do you know why?'.

**Script:** "[Acknowledge_ResponseToWhy_Briefly] Because thousands of students already generated over 20,000 per month and our best student John is doing over 1 million per month with it. I'm not saying you're going to get to his level... but is this range of passive income something that may be worth exploring in your opinion?"

**Transitions:**
- still_interested → N_IntroduceModel_And_AskQuestions_V3_Adaptive
- default → N_IntroduceModel_And_AskQuestions_V3_Adaptive

### N_Obj_EarlyDismiss_DirectValueChallenge_V9_EscalationEnabled
**Goal:** To deliver a direct, challenging value hook to reignite curiosity.

**Context:** You are entering this node after softer re-engagement attempts have failed.

**Script:** "if I shared with you a real shot at an extra 20,000 a month passively would you keep talking to me?"

**Transitions:**
- still_interested → N_Obj_EarlyDismiss_ConnectToCurrentCall_V5_LeadOut
- default → N_Obj_EarlyDismiss_ConnectToCurrentCall_V5_LeadOut

### N_Obj_EarlyDismiss_ConnectToCurrentCall_V5_LeadOut
**Goal:** To enthusiastically confirm to {{customer_name}} that this call is indeed about the significant income potential previously hinted at, and then to directly ask if exploring that potential is worth their consideration.

**Context:** You are entering this node after the user showed curiosity in response to the '$20k challenge' hook.

**Script:** "That's exactly what the next couple of minutes are about! So, is a range of 20,000 up to a million a month in passive income something that may be worth exploring in your opinion?"

**Transitions:**
- exploration_agreed → N_IntroduceModel_And_AskQuestions_V3_Adaptive
- default → N_IntroduceModel_And_AskQuestions_V3_Adaptive

### N_Obj_RealBusy_BluntCheck_V3_Adaptive
**Goal:** To assertively diagnose whether the user's 'I'm busy' objection is a genuine time constraint or a polite dismissal due to a lack of perceived value.

**Context:** You are entering this node mid-call after the user has raised a time-based objection.

**Script:** "Let me be blunt. Are you not sure why you should be listening to this, or is there a meeting coming up for you right now?"

**Transitions:**
- meeting_coming_up → N_Obj_RealBusy_AskMeetingTime
- not_sure_why_listening → N_Obj_RealBusy_OfferReschedule
- default → N_Obj_RealBusy_OfferReschedule

### N_Obj_RealBusy_AskMeetingTime
**Goal:** Acknowledge their upcoming meeting and ask specifically how long until their meeting.

**Context:** Entered from N_Obj_RealBusy_BluntCheck after the prospect confirmed they have an actual meeting.

**Script:** "No problem. In how long is your meeting?"

**Transitions:**
- time_given → N_Obj_RealBusy_StateRemainingTimeAndWrapUp
- vague → N_Obj_RealBusy_OfferReschedule
- default → N_Obj_RealBusy_OfferReschedule

### N_Obj_RealBusy_StateRemainingTimeAndWrapUp
**Goal:** Acknowledge the meeting timeframe, state the calculated remaining time, and signal intent to quickly wrap up.

**Context:** Entered from N_Obj_RealBusy_AskMeetingTime after prospect provided their meeting timeframe.

**Script:** "Okay. That means we have [Calculated_Remaining_Time, e.g., 'about 5 minutes'] then. Let me wrap this up for you..."

**Transitions:**
- default → N_Opener_StackingIncomeHook_V3_CreativeTactic

### N_Obj_RealBusy_OfferReschedule
**Goal:** If the prospect indicates no time *now*, acknowledge and ask when would be a better time to talk later.

**Context:** Entered if prospect confirms no time now.

**Script:** "No problem. When will be a better time to talk later?"

**Transitions:**
- default → N_Obj_RealBusy_ConfirmRescheduleTime

### N_Obj_RealBusy_ConfirmRescheduleTime
**Goal:** Reiterate the exact reschedule time the prospect offered and ask for 100% confirmation.

**Context:** Entered from N_Obj_RealBusy_OfferReschedule after the prospect suggested a reschedule time.

**Script:** "So what you are saying is that you will be 100% available at [EXACT TIME PROSPECT OFFERED]?"

**Transitions:**
- confirmed → N_Obj_RealBusy_StateCallbackAndTeaseGuarantees
- default → N_Obj_RealBusy_StateCallbackAndTeaseGuarantees

### N_Obj_RealBusy_StateCallbackAndTeaseGuarantees
**Goal:** Confirm the AI will call back at the agreed time, tease the 3 guarantees, and ask if exploring them would be worthwhile.

**Context:** Entered from N_Obj_RealBusy_ConfirmRescheduleTime after prospect confirmed 100% availability.

**Script:** "Great. I'll call you back at [CONFIRMED TIME]. Btw keep in mind... we have 3 guarantees because this really does work... and one guarantee is an ROI guarantee, which means it's about getting your money back. Would that be something worth exploring?"

**Transitions:**
- worth_exploring → N_ConfirmCommitment_FinalCheck_V1_Adaptive
- default → N_ConfirmCommitment_FinalCheck_V1_Adaptive

## 9. Objection Engine Rules (A2/A3/A4)

The agent first detects an objection using the [`_contains_objection()`](caller_agent.py:2012) method in [`caller_agent.py`](caller_agent.py). Once an objection is detected, the [`ObjectionHandler`](objection_handler.py) takes over with the following rules and discipline:

Reply constraints and rotation discipline for the objection-handling engine:
- Length: 1–2 sentences maximum per reply.
- Forbidden “easy-outs” (denylisted examples): “I can’t help with that.”, “Maybe later.”, “It depends.”, “I’m not sure.”, “Let’s circle back.”, “We’ll see.”, “I don’t know.”, “Sorry, I can’t.”, “That’s complicated.”, “Not possible.”
- Rotation freshness: enforced per `thread_id` × `persona` × `node_id` × `objection_cat`. Do not repeat the same angle within that scope.
- Mandatory pivot: re-anchor to the node MVP goal using a fresh rephrase from the pivot bank. For D-personality, exact pivot phrases from the `MVP_GOALS` bank are prioritized and preserved during sentence capping. This is enforced by [`ObjectionHandler.enforce_pivot()`](objection_handler.py:1581).
- Optional concise KB splice: at most 120 characters and ≤2 sentences; must carry valid tags (`node_id`/`topic`[/`persona`]).
- Escalation: reverse-psychology test is permitted only after distinct angles have been exhausted within the thread and only when gated ON.

## 10. Feature Flags and AB Guard

Flags topology (all defaults OFF unless specified):
- [`FLAGS['engine_global']`](objection_handler.py:20): default `False`
- [`FLAGS['ab_guard']['enabled']`](objection_handler.py:21): default `True`
- [`FLAGS['ab_guard']['percent']`](objection_handler.py:21): default `0`
- [`FLAGS['nodes'][node_id][persona]`](objection_handler.py:24): default `False` for each persona (D/I/S/C) per `node_id`

AB cohort selection:
- Deterministic selection: `SHA256(thread_id) % 100 <= percent` (implemented in [`_ab_cohort()`](objection_handler.py:1451) in [`objection_handler.py`](objection_handler.py))
- When [`FLAGS['ab_guard']['enabled']`](objection_handler.py:21) is `True`, only selected cohort routes through the new engine; others use the legacy path.
- Safety: If [`FLAGS['engine_global']`](objection_handler.py:20) is `False` or node/persona flag is `False` or cohort not selected, the legacy path remains intact. This logic is encapsulated in [`should_use_new_engine()`](objection_handler.py:1460) in [`objection_handler.py`](objection_handler.py).

Explicit defaults:
- All flags are OFF by default. No personas or nodes are active unless explicitly enabled.
- IntroduceModel can be canary-enabled for I/D personas via node-level persona flags (see examples below).

## 11. Activation Matrix (Node × Persona)

Status defaults: OFF for all unless explicitly enabled. Notes column highlights staged rollout cues.

| Node (node_id)       | D | I | S | C | Status (default) | Notes |
|----------------------|---|---|---|---|------------------|-------|
| IntroduceModel       | OFF | OFF | OFF | OFF | OFF | B1 canary: IntroduceModel I→D first |
| KB_QA                | OFF | OFF | OFF | OFF | OFF | A3 snippets available; engine gated |
| IncomeBackground     | OFF | OFF | OFF | OFF | OFF | Follows IntroduceModel activation |
| FinancialQualification| OFF | OFF | OFF | OFF | OFF | AB guard required before enable |
| Commitment           | OFF | OFF | OFF | OFF | OFF | Keep legacy logic when OFF |
| Scheduling           | OFF | OFF | OFF | OFF | OFF | Legacy scheduling intact |

Example: enable B1 canary for IntroduceModel I or D at 10% cohort (copy-paste):
```
from [`objection_handler`](objection_handler.py) import `FLAGS`
`FLAGS['engine_global']` = `True`
`FLAGS['nodes']['IntroduceModel']['I']` = `True`
# Optionally enable D next:
# `FLAGS['nodes']['IntroduceModel']['D']` = `True`
`FLAGS['ab_guard']['enabled']` = `True`
`FLAGS['ab_guard']['percent']` = `10`
```

Determinism note:
- Cohort is deterministic by thread_id hashing; the same thread_id will always route the same way at a given percent.

## 12. Node MVP Goals and Pivot Banks

Rephrase freshness is enforced per `thread_id` × `node_id` to avoid repetition, managed by [`ObjectionHandler.get_fresh_pivot()`](objection_handler.py:1498). Use these as pivot anchors after addressing the objection.

| node_id             | MVP goal                                                                 | pivot_bank (4–6 fresh rephrases) |
|---------------------|---------------------------------------------------------------------------|-----------------------------------|
| IntroduceModel      | Deliver concise model summary and elicit initial thoughts/concerns        | "Let me restate the core: we deploy sites that earn; what stands out to you?", "In short, it’s a site-based cashflow engine—what’s your first concern?", "Boiled down: assets online that pay you—what questions pop up first?", "Net-net: set up, rank, and collect—what’s the biggest unknown for you?", "The gist is passive sites producing income—where does your mind go?", "Essentially: digital real estate for yield—what’s your first reaction?" |
| KB_QA               | Answer targeted questions with concise, tagged KB evidence                | "Quick fact that helps: [concise snippet]. Given that, what’s still unclear?", "Here’s the key data point: [concise snippet]. What part should we zoom in on?", "Given this detail: [concise snippet], what remains the blocker?", "Short answer with context: [concise snippet]. What else would help?", "Compact proof: [concise snippet]. Where should we go next?", "Core takeaway: [concise snippet]. Does that address your worry?" |
| IncomeBackground    | Establish employment context and income references                        | "So with that context, what would make this worth it for you monthly?", "Given your current lane, what’s a realistic new stream target?", "Based on what you shared, what income range would feel meaningful?", "Considering your workload, what return would justify this?", "With your role in mind, what output moves the needle?", "Anchoring to your numbers, what’s a good starting benchmark?" |
| FinancialQualification | Confirm capital/credit fit to proceed                                 | "To move forward, we just need to confirm capital—does that fit?", "At minimum, we’d verify either capital or credit—where do you stand?", "The next step is a quick capital check—should we go there?", "We can route by capital or credit—what’s the better path?", "We only need a simple yes/no on funds—how’s that looking?", "If not cash, credit works too—want to confirm?" |
| Commitment          | Secure verbal commitment to show up                                      | "Aside from emergencies, anything that would stop you from attending?", "To keep it firm, are you comfortable locking that in now?", "So we’re solid on that slot—any conflicts we should resolve?", "To respect your time, can we consider that confirmed?", "Just to be sure, are you fully available then?", "Let’s lock it: any reason that time wouldn’t work?" |
| Scheduling          | Gather timezone and confirm a precise appointment                         | "What timezone should I plan around?", "When are you typically at your desk?", "What precise time window works best?", "Does that time fit a Zoom from your computer?", "Should we adjust if a partner must join?", "Let’s put the exact time on the calendar now." |
|                     |                                                                           |                                   |

Usage:
- When an objection lands, respond in 1–2 sentences, then immediately pivot with a fresh rephrase toward the node’s MVP goal. This is enforced by [`ObjectionHandler.enforce_pivot()`](objection_handler.py:1581). Do not reuse a pivot within the same thread/node.

## 13. Logging Schema (A2)

Structured event emitted by the objection engine:
```
{
  `thread_id`: `str`,
  `node_id`: `str`,
  `persona`: `"D" | "I" | "S" | "C"`,
  `objection_cat`: `str`,
  `occurrence`: `int`,           # nth time this objection_cat seen in thread
  `angle_index`: `int`,          # which unique angle was used this time
  `pivot_id`: `str`,             # id/key of pivot rephrase selected
  `kb_snippet_id`: `str | null`, # concise snippet id if spliced
  `escalation`: {              # reverse-psychology gate
    `enabled`: `bool`,
    `fired`: `bool`,
    `step`: `int | null`         # which step in escalation ladder
  }
}
```

Sample log lines
- Legacy path (`FLAGS` OFF by default):
```json
{"thread_id":"t_123","node_id":"IntroduceModel","persona":"I","route":"legacy","note":"engine_off"}
```
- Engine path (`FLAGS` ON and cohort selected):
```json
{"thread_id":"t_123","node_id":"IntroduceModel","persona":"I","route":"engine","objection_cat":"risk","occurrence":2,"angle_index":1,"pivot_id":"IM_v2_p4","kb_snippet_id":"kb_IM_risk_07","escalation":{"enabled":false,"fired":false,"step":null}}
```

Assurances:
- No PII in logs.
- Deterministic and reproducible by thread seed and hashing rules.

## 14. KB Concise Snippets (A3)

Tag schema for concise snippets:
- id: str
- text: ≤120 chars, ≤2 sentences
- tags: { node_id, topic, persona|null }

Retrieval API behavior (implemented in [`kb_processor.py`](kb_processor.py)):
```python
get_concise_snippet(
  node_id: str,
  topic: str,
  persona_or_none: str | None,
  max_len: int = 120,
  max_sents: int = 2,
  seed_keys: tuple | None = None
) -> dict | None
```
Selection & fallback:
- Try (a) node_id + topic + persona
- Else (b) node_id + topic
- Else (c) topic-only
- Deterministic selection via stable hash modulo candidate count; respects max_len and max_sents.

CLI validator commands (copy-paste, using [`preprocess_kb.py`](preprocess_kb.py)):
```bash
python preprocess_kb.py --input data/doc_chunks.json --output data/kb_index.faiss --validate-only
python preprocess_kb.py --input data/doc_chunks.json --output data/kb_index.faiss --rebuild
```

## 15. Testing & CI Gates (A4)

Behavioral tests summarized:
- Sentence cap ≤2 on responses.
- Denylist CI guard for “easy-outs”.
- Pivot presence and per-thread/node freshness.
- Rotation determinism for angles and pivots.
- DISC tone marker injection gating present.
- AB guard routing: cohort vs legacy.
- KB validator correctness; snippet caps/tag relevance enforced.
- get_concise_snippet determinism/fallback/caps validated.
- Integration flow for IntroduceModel with flags toggled (legacy vs engine).

CI guidance:
- Any denylist or sentence-cap failure blocks merges.
- Tests must run with deterministic seeds to ensure reproducible rotations.

## 16. Escalation Policy

- Reverse-psychology test is triggered only after distinct angles have been exhausted for the same objection category within a thread.
- Escalation is gated by a feature flag (default OFF).
- Tone must remain calm and neutral; escalation events are logged with escalation.enabled/fired/step.

## 17. Acceptance Criteria & Rollout Plan

Acceptance per node (applies to IntroduceModel, KB_QA, IncomeBackground, FinancialQualification, Commitment, Scheduling):
- Correct objection categorization.
- Replies are 1–2 sentences; no denylisted “easy-outs”.
- Mandatory pivot to node MVP goal using a fresh rephrase (freshness enforced).
- Rotation freshness across angles and pivots per thread/persona/node/objection.
- Persona tone markers respected (D/I/S/C).
- KB snippet (if used) ≤120 chars, ≤2 sentences, proper tags, relevance.
- Escalation only after angles exhausted and properly logged.

Rollout plan (B1→B6):
- B1 canary: IntroduceModel (start with I, then D) while S/C remain OFF.
- AB guard percent small (e.g., 10%) with deterministic cohorting.
- Observe logs for rotation, pivot freshness, and denylist/length compliance before expanding.
- Subsequent waves add KB_QA, then IncomeBackground, FinancialQualification, Commitment, Scheduling.

Where to enable B1 canary (copy-paste from Section 11):
```
from objection_handler import FLAGS
FLAGS['engine_global'] = True
FLAGS['nodes']['IntroduceModel']['I'] = True
# Optionally enable D next:
# FLAGS['nodes']['IntroduceModel']['D'] = True
FLAGS['ab_guard']['enabled'] = True
FLAGS['ab_guard']['percent'] = 10
```

Operational reminder:
- Engine defaults are OFF. Canary-enable narrowly and validate via logs and CI before widening.

## 18. Safety, Flags, and Observability Playbook

Operational runbook for safe activation, measurement, and rollback of the objection-handling engine.

1) Flags
- Defaults (all OFF unless explicitly enabled):
  - engine_global=False
  - ab_guard.enabled=True
  - ab_guard.percent=0
  - nodes[node_id][persona] False for all personas per node
- 10% canary example (IntroduceModel, personas I and D):
  ```
  from objection_handler import FLAGS
  FLAGS['engine_global'] = True
  FLAGS['nodes']['IntroduceModel']['I'] = True
  FLAGS['nodes']['IntroduceModel']['D'] = True
  FLAGS['ab_guard']['enabled'] = True
  FLAGS['ab_guard']['percent'] = 10
  ```
- Ramp to 100%:
  - Increase FLAGS['ab_guard']['percent'] → 50 → 100 after stable observations (≥24h).
- Kill-switch procedure:
  - Global rollback: set FLAGS['engine_global'] = False (all traffic to legacy).
  - Scoped rollback: set FLAGS['nodes'][node_id][persona] = False OR reduce FLAGS['ab_guard']['percent'] to last stable.
  - Confirm via logs route=="legacy" for impacted scopes.

2) AB Guard
- Deterministic cohorting:
  - cohort(thread_id) = SHA256(thread_id) % 100
  - Engine used when cohort < FLAGS['ab_guard']['percent'] and other flags allow.
- Impact:
  - Reproducibility: same thread_id will consistently route the same way for a given percent.
  - Observability: Log cohort and percent to correlate outcomes.

3) Logging
- Structured fields (engine path):
  - { thread_id, node_id, persona, objection_category, occurrence, angle_index, pivot_id, kb_snippet_id, route, flags_snapshot, ab_guard{enabled,percent,cohort}, escalation{enabled,fired,step}, timings }
- Sample log lines
  - Legacy:
    ```
    {"route":"legacy","thread_id":"t1","node_id":"IntroduceModel","persona":"D","note":"engine_off"}
    ```
  - Engine:
    ```
    {"route":"engine","thread_id":"t1","node_id":"IntroduceModel","persona":"D","objection_category":"skeptical_roi","occurrence":1,"angle_index":2,"pivot_id":"IM_goal_01","kb_snippet_id":null,"ab_guard":{"enabled":true,"percent":10,"cohort":7},"flags":{"engine_global":true,"kb_splice":false}}
    ```
- Sinks and PII safeguards
  - Centralize logs (e.g., CloudWatch/ELK/GCP Logging).
  - Redact PII; use hashed thread_id only.
  - For verbose debug events, sample at 10–20%; keep route, node_id, persona, occurrence, angle_index always.
- Dashboard queries (examples)
  - Activation rate by node/persona: filter route=="engine"; group by node_id, persona; plot over time.
  - Denylist hits: where easy_out_flag==true; group by node_id/persona.
  - Length violations: where sentence_count>2 OR char_count>280.
  - Rotation freshness: distribution of angle_index by occurrence per node/category/persona.

4) Runtime Checks
- Expectations enforced by CI (see Section 20):
  - Sentence cap: ≤2.
  - Denylist: no “easy-outs”.
- Triage runbook for violations
  - Immediate: rollback to last stable cohort or disable the affected node/persona flags.
  - Diagnose: filter logs by node_id/persona and objection_category; identify offending angles or pivots.
  - Fix: update BANKS for the category/persona; re-run tests; re-enable canary.

5) KB splice policy
- Default OFF:
  - Keep FLAGS['kb_splice'] = False; engine runs without snippet insertion.
- Enable safely (per node/persona)
  - Validate KB: 
    ```
    python preprocess_kb.py --input data/doc_chunks.json --output data/kb_index.faiss --validate-only
    ```
  - Set FLAGS['kb_splice'] = True and keep ab_guard.percent at 10 initially.
  - Verify logs contain kb_snippet_id and snippets respect caps/tags.
  - Expand percent after stable metrics.

6) Escalation policy
- Default OFF:
  - Reverse-psychology escalation remains disabled.
- Gate to ON only after:
  - Distinct-angle exhaustion behavior validated in tests.
  - Create watch metric: escalation.fired count per 100 engine replies.
- Rollback:
  - Set FLAGS['escalation'] = False; confirm escalation.fired=false in logs.

---

## 19. Engineering Task Graph (File/Function-Level)

Dependency-ordered checklist to extend or onboard new nodes.

A2 — Caller plumbing & enforcement (implemented)
- Entry points and helpers
  - handle objection flow and structured logging in objection engine file.
  - Enforce reply constraints with [`objection_handler.py.enforce_pivot()`](objection_handler.py:1581).
  - Deterministic rotation via [`objection_handler.py.deterministic_index()`](objection_handler.py:1273).
  - Caller propagation and thread seeding in [`caller_agent.py`](caller_agent.py).
- How to extend
  - Add thread_id/node_id/persona propagation if introducing new callers.
  - Emit new fields by extending engine log payload consistently.

A3 — KB layer (implemented)
- Validator CLI in [`preprocess_kb.py`](preprocess_kb.py).
- Deterministic retrieval with fallbacks in [`kb_processor.py.get_concise_snippet()`](kb_processor.py).
- Adding topics/tags
  - Ensure tags include node_id, topic, and optional persona.
  - Re-run validator (validate-only), then rebuild if indexes used.

A4 — Tests (implemented)
- Add tests for a new node/category/persona:
  - Seed fixed thread_id; assert: 1–2 sentences; denylist clean; pivot present; rotation stable; tone marker minimal.
  - Files: [`test_objection_engine_basics.py`](tests/test_objection_engine_basics.py), [`test_integration_objection_flow.py`](tests/test_integration_objection_flow.py), [`test_kb_concise_snippets.py`](tests/test_kb_concise_snippets.py).

A5 — Docs (implemented)
- Extend [`complete_conversation_script.md`](complete_conversation_script.md) with node pivots and activation notes.
- Link to specific helpers as syntax references: [`objection_handler.py.enforce_pivot()`](objection_handler.py:1581), [`kb_processor.py.get_concise_snippet()`](kb_processor.py).

B-waves — Onboarding a new node (step-by-step)
1) Add MVP_GOALS (goal + pivot_bank)
   - Define fresh pivot_bank (≥4–6 variants) under the node’s namespace.
2) Add node_id normalization helper
   - Map aliases to canonical node_id in the engine file.
3) Add map_<node>_category()
   - Deterministically bucket objections to categories.
4) Add BANKS[node][persona][category]
   - Each category must have ≥4 distinct angles per persona to ensure rotation freshness.
5) Wire rotation, pivot enforcement, structured logs
   - Use [`objection_handler.py.deterministic_index()`](objection_handler.py:1273) and [`objection_handler.py.enforce_pivot()`](objection_handler.py:1581).
   - Emit log fields described in Section 18.
6) Optional kb_splice topic mapping (keep OFF initially)
   - Align topic keys with categories; leave FLAGS['kb_splice']=False until validated.
7) Add minimal integration test
   - Fix seed, toggle flags for canary, assert constraints and logging fields.

---

## 20. Acceptance Gates & Definition of Done (DoD)

Per-node acceptance criteria
- Categorization: Correct for fixture objections.
- Reply constraints: 1–2 sentences; no denylisted “easy-outs”.
- Pivot: Present and fresh relative to thread/node occurrence.
- Rotation: Next angle chosen deterministically per occurrence.
- Persona tone: Minimal DISC markers, aligned with persona.
- KB splice (if enabled): ≤120 chars, ≤2 sentences, correct tags; kb_snippet_id logged.
- Escalation: OFF by default; not firing in logs.

CI/Test gates (blocking)
- Denylist and sentence-cap tests in [`test_objection_engine_basics.py`](tests/test_objection_engine_basics.py) must pass.
- Integration tests in [`test_integration_objection_flow.py`](tests/test_integration_objection_flow.py) must pass.
- KB validator tests in [`test_kb_concise_snippets.py`](tests/test_kb_concise_snippets.py) must pass.

PR scope templates
- Node-only PR
  - Changes: BANKS additions, map_<node>_category, normalization.
  - Include: new/updated tests, before/after sample outputs, planned flag settings (node/persona and percent).
- Test-only PR
  - Changes confined to tests; no flags or engine logic changes.
- Docs-only PR
  - Update [complete_conversation_script.md](complete_conversation_script.md) and/or ops notes; no runtime impact.

Rollout checklist per canary
- Pre-flight
  - All tests green; KB validator clean; flags staged but percent=0.
- Enable
  - engine_global=True; node/persona=True; percent=10.
- Observe (≥24h)
  - route=="engine" rate; denylist/length violations; angle rotation freshness; pivot presence rate; errors.
- Expand
  - percent→50→100 as long as metrics stable and no regressions.
- Rollback
  - Reduce percent to last stable, or disable node/persona flag, or engine_global=False.
  - Confirm route=="legacy" for affected scope.

---

## 21. Risk Log with Mitigations

Loop risk / pivot failure / repetition
- Mitigations: Enforce pivot via [`objection_handler.py.enforce_pivot()`](objection_handler.py:1581); ensure ≥4 angles per category; test rotation determinism with fixed seeds.

Legacy regression
- Mitigations: Default FLAGS off; AB guard staged; global kill-switch; integration tests to protect legacy behavior.

DISC misclassification / tone mismatch
- Mitigations: Minimal tone markers; fallback to neutral when persona unknown; add tests for tone gating.

KB data gaps / invalid tags / long snippets
- Mitigations: Run validator CLI before enabling splice; runtime caps in [`kb_processor.py.get_concise_snippet()`](kb_processor.py); fallback to no-splice and log null kb_snippet_id.

Log volume / PII / observability gaps
- Mitigations: Centralize logs; sample verbose contexts; redact PII; hash thread_id; build dashboards outlined in Section 18.

Test flakiness / nondeterminism
- Mitigations: Seed with thread_id; deterministic_index checks; CI uses fixed seeds and stable occurrence counters.

Overfitting angle banks / stale pivots
- Mitigations: Quarterly review of BANKS; add diverse angles; monitor success metrics; refresh pivot_bank regularly; block merges if denylist/length violations appear.
