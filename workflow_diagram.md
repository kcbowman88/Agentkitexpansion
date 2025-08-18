graph TD
    A[N001A_NameConfirmation_Only] --> B[N001B_IntroAndHelpRequest_Only]
    B --> C[N_Opener_StackingIncomeHook_V3_CreativeTactic]
    
    C -->|agrees| D[N_IntroduceModel_And_AskQuestions_V3_Adaptive]
    C -->|no_recall| E[N003_NoRecall_PivotAndChallenge_V18_FullyTuned]
    C -->|objection| F[N003B_DeframeInitialObjection_V7_GoalOriented]
    C -->|not_interested| G[N_Obj_EarlyDismiss_AskShareBackground_V7]
    C -->|no_time| H[N_Obj_RealBusy_BluntCheck_V3_Adaptive]
    C -->|question| I[N_KB_Q&A_With_StrategicNarrative_V3_Adaptive]
    C -->|default| D
    C -->|personality_D| D_D[N_IntroduceModel_And_AskQuestions_V3_Adaptive_Dominant]
    C -->|personality_I| D_I[N_IntroduceModel_And_AskQuestions_V3_Adaptive_Influential]
    C -->|personality_S| D_S[N_IntroduceModel_And_AskQuestions_V3_Adaptive_Steady]
    C -->|personality_C| D_C[N_IntroduceModel_And_AskQuestions_V3_Adaptive_Conscientious]
    
    H -->|meeting_coming_up| J[N_Obj_RealBusy_AskMeetingTime]
    H -->|not_sure_why_listening| K[N_Obj_RealBusy_OfferReschedule]
    H -->|default| K
    
    J -->|time_given| L[N_Obj_RealBusy_StateRemainingTimeAndWrapUp]
    J -->|vague| K
    J -->|default| K
    
    K --> M[N_Obj_RealBusy_ConfirmRescheduleTime]
    M --> N[N_Obj_RealBusy_StateCallbackAndTeaseGuarantees]
    N --> O[N_ConfirmCommitment_FinalCheck_V1_Adaptive]
    
    L --> C
    O --> D
    
    D --> I
    D_D --> I
    D_I --> I
    D_S --> I
    D_C --> I
    
    I --> P[N200_Super_WorkAndIncomeBackground_V3_Adaptive]
    P -->|employed| Q[N201A_Employed_AskYearlyIncome_V8_Adaptive]
    P -->|business_owner| R[N202A_AskCurrentMonthlyRevenue_V7_FullyTuned]
    P -->|unemployed| S[N201E_Unemployed_EmpathyAskPastYearlyIncome_V5_Adaptive]
    P -->|default| Q
    P -->|personality_D| P_D[N200_Super_WorkAndIncomeBackground_V3_Adaptive_Dominant]
    P -->|personality_I| P_I[N200_Super_WorkAndIncomeBackground_V3_Adaptive_Influential]
    P -->|personality_S| P_S[N200_Super_WorkAndIncomeBackground_V3_Adaptive_Steady]
    P -->|personality_C| P_C[N200_Super_WorkAndIncomeBackground_V3_Adaptive_Conscientious]
    
    Q --> T[N201B_Employed_AskSideHustle_V4_FullyTuned]
    T -->|yes| U[N201C_Employed_AskSideHustleAmount_V3_FullyTuned]
    T -->|no| V[N201D_Employed_AskVehicleQ_V5_Adaptive]
    T -->|default| V
    
    P_D --> Q
    P_I --> Q
    P_S --> Q
    P_C --> Q
    
    style H fill:#f9f,stroke:#333
    style K fill:#f9f,stroke:#333
    style J fill:#f9f,stroke:#333
    style L fill:#f9f,stroke:#333
    
    classDef problemArea fill:#f9f,stroke:#333;
    class H,K,J,L problemArea;
    
    classDef personalityVariant fill:#e1f5fe,stroke:#01579b;
    class D_D,D_I,D_S,D_C,P_D,P_I,P_S,P_C personalityVariant;