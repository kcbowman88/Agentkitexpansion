graph TD
    subgraph "1. Opening & Triage"
        A["N001A NameConfirmation"] -->|Confirm Name| B["N001B IntroAndHelpRequest"]
        B -->|Request Help| C["N_Opener StackingIncomeHook"]
        C -->|Agrees to talk| G["N_IntroduceModel And AskQuestions"]
        C -->|No Recall| E["N003 NoRecall PivotAndChallenge"]
        C -->|General Objection| D["N003B DeframeInitialObjection"]
        C -->|Not Interested| F["N_Obj EarlyDismiss AskShareBackground"]
        C -->|No Time| AA["N_Obj RealBusy BluntCheck"]
    end

    subgraph "2. Main Path - Explanation & Qualification"
        G --> H["N_KB QandA With StrategicNarrative"]
        E -->|Shows interest| G
        H --> I["N200 Super WorkAndIncomeBackground"]
        I -->|Employed| J["N201A Employed AskYearlyIncome"]
        I -->|Business Owner| M["N202A AskCurrentMonthlyRevenue"]
        I -->|Unemployed| K["N201E Unemployed EmpathyAskPastYearlyIncome"]
    end

    subgraph "3. Dismissal & Busy Loops"
        subgraph "Early Dismissal Path"
            F -->|Agrees| F1["N_Obj EarlyDismiss ShareBackground DeliverStoryHook"]
            F1 --> AB["N_Obj EarlyDismiss ShareBackgroundAskWhy"]
            AB --> AD["N_Obj EarlyDismiss ExplainReasonAndExplore"]
            AD -->|Still interested| G
            F -->|Declines| AC["N_Obj EarlyDismiss DirectValueChallenge V1"]
            AC --> AE["N_Obj EarlyDismiss ConnectToCurrentCall V1"]
            AE -->|Agrees to explore| G
        end
        subgraph "Busy Loop"
            AA --> AF["N_Obj RealBusy AskMeetingTime"]
            AF -->|Time Given| AG["N_Obj RealBusy StateRemainingTimeAndWrapUp"] --> C
            AF -->|Vague| AH["N_Obj RealBusy OfferReschedule"]
            AH --> AI["N_Obj RealBusy ConfirmRescheduleTime"]
            AI --> AJ["N_Obj RealBusy StateCallbackAndTeaseGuarantees"] --> BD
        end
    end

    subgraph "4. Income & Vehicle Questions"
        J --> L["N201B Employed AskSideHustle"]
        L -->|Yes| O["N201C Employed AskSideHustleAmount"] --> R["N201D Employed AskVehicleQ"]
        L -->|No| R
        M --> P["N202B AskHighestRevenueMonth"] --> S["N202C AskVehicleQuestion BusinessOwner"]
        K --> N["N201F Unemployed AskSideHustle"]
        N -->|Yes| Q["N201G Unemployed AskSideHustleAmount"] --> T["N201H Unemployed AskVehicleQ"]
        N -->|No| T
    end

    subgraph "5. Financial Qualification"
        R --> V{Vehicle Q Affirmed}
        S --> V
        T --> V
        V -->|Yes| V_Check{"Income > 8k"}
        V_Check -->|Yes| V_Node["N_AskCapital 15k"]
        V_Check -->|No| U["N_AskCapital 5k Direct"]
        V_Node -->|Has 15-25k| AX["N_ConfirmCommitment FinalCheck"]
        V_Node -->|No| U2["N_AskCapital 5k from 15k"]
        U -->|Has 5k| AX
        U -->|No| W["N205C AskCreditScore 650"]
        U2 -->|Has 5k| AX
        U2 -->|No| W
        W -->|Score > 650| AX
        W -->|Score < 650| W_End["Disqualified"]
    end

    subgraph "6. Motivation & Scheduling Proposal"
        AX --> X["N401 AskWhyNow Initial"]
        X --> Y["N402 Compliment And AskYouKnowWhy"]
        Y --> Z["N403 IdentityAffirmation And ValueFitQuestion"]
        Z --> AK["N500A ProposeDeeperDive"]
    end

    subgraph "7. Scheduling Logistics"
        AK --> AL["N500B AskTimezone"]
        AL --> AM["N_AskForCallbackRange"]
        AM --> AN["N_Scheduling AskTime SmartAmbiguity"]
        AN --> AO["N_ConfirmVideoCallEnvironment"]
        AO --> AQ["N206 AskAboutPartners"]
        AQ -->|Partner| AR["N018 ConfirmPartnerAvailability"]
        AQ -->|No Partner| AY_Confirm["N_ConfirmCommitment_FinalCheck_V1_Adaptive"]
        AR -->|Available| AY_Confirm["N_ConfirmCommitment_FinalCheck_V1_Adaptive"]
        AR -->|Not Available| AP["N_Scheduling RescheduleAndHandle"]
        AR -->|Unsure| AS["N017D SuggestPartnerCheck ScheduleFollowUpCall"]
        AP -->|New Time Found| AY_Confirm
    end

    subgraph "8. Final Confirmation & Close"
        AY_Confirm --> AT["N_AskAboutReminderSetup"]
        AT --> AU["N_CheckForTextReceipt"]
        AU --> AW["N_ConfirmAndRequestReply"]
        AW --> AY["N_Video Assign GentleIntro"]
        AY --> AZ["N_Video ReinforceValue FeeContext"]
        AZ --> BA["N_Video RelateSocialProof"]
        BA --> BB["N_Video AssignAndCommit"]
        BB --> BC["N_Video ConfirmAndReply"]
        BC --> AV["N_Finalize And EndCall V1"]
        AV --> BD["N_EndCall Final Decisive"]
    end
