# Nodes Master Checklist

Test Policy Summary
- Zero exits anywhere: agent must persist and progress toward node goals; no dead-ends mid-flow
- Anti-repetition strict: enforce both exact sentence duplication and near-duplicate detection with 6-gram similarity across the entire conversation and within a single turn; bridges and acknowledgments must vary
- Strict goal gating: transition only when the node’s goal is verifiably achieved
- Contextual bridge: after objections/Q&A detours, include a contextual bridge before resuming node objective
- End-to-end success: must include booking confirmed and homework video commitment

Legend
- Each canonical node has one checkbox for Tested
- Variants are nested; inherit the canonical node’s test status unless explicitly split in future

## 1. Opening & Triage


N_Opener_StackingIncomeHook_V3_CreativeTactic
- Goal: Deliver stacking income hook and get 25s permission
- Cue: ...stacking income without stacking hours... do you have just 25 seconds...
- Transitions: permission_granted → N_IntroduceModel_And_AskQuestions_V3_Adaptive; no_recall → N003_NoRecall_PivotAndChallenge_V18_FullyTuned; objection_or_callback_request → N003B_DeframeInitialObjection_V7_GoalOriented; not_interested → N_Obj_EarlyDismiss_AskShareBackground_V7; no_time → N_Obj_RealBusy_BluntCheck_V3_Adaptive; question → N_KB_Q&A_With_StrategicNarrative_V3_Adaptive; default → N_IntroduceModel_And_AskQuestions_V3_Adaptive; personality_D/I/S/C → corresponding variants; context_high_engagement → ..._HighEngagement; context_low_engagement → N_Obj_EarlyDismiss_AskShareBackground_V7
- [ ] Tested — Notes:

## 2. Main Path — Explanation & Qualification

N_IntroduceModel_And_AskQuestions_V3_Adaptive
- Goal: Concise model summary; elicit initial thoughts/concerns
- Cue: In a nutshell, we set up passive income websites...
- Transitions: default → N_KB_Q&A_With_StrategicNarrative_V3_Adaptive
- Variants:
  - N_IntroduceModel_And_AskQuestions_V3_Adaptive_Dominant — Cue: ...what's the biggest concern...
  - N_IntroduceModel_And_AskQuestions_V3_Adaptive_Influential — Cue: ...Isn't that exciting? What aspects...
  - N_IntroduceModel_And_AskQuestions_V3_Adaptive_Steady — Cue: ...Take your time... What questions come to mind...
  - N_IntroduceModel_And_AskQuestions_V3_Adaptive_Conscientious — Cue: ...I can provide more detailed information... What specific aspects...
  - N_IntroduceModel_And_AskQuestions_V3_Adaptive_HighEngagement — Cue: ...Since you seem interested, what specific aspects...
- [ ] Tested — Notes:

N_KB_Q&A_With_StrategicNarrative_V3_Adaptive
- Goal: Dynamically answer questions; ensure income potential discussed; deliver $20k value-framing question
- Cue: Dynamic KB-driven response with adaptive closing question
- Transitions: default → N200_Super_WorkAndIncomeBackground_V3_Adaptive
- [ ] Tested — Notes:

N200_Super_WorkAndIncomeBackground_V3_Adaptive
- Goal: Determine employment status (employee vs owner vs unemployed)
- Cue: ...are you working for someone or do you run your own business?
- Transitions: employed → N201A_Employed_AskYearlyIncome_V8_Adaptive; business_owner → N202A_AskCurrentMonthlyRevenue_V7_FullyTuned; unemployed → N201E_Unemployed_EmpathyAskPastYearlyIncome_V5_Adaptive; default → N201A_Employed_AskYearlyIncome_V8_Adaptive; personality_D/I/S/C → respective variants
- Variants:
  - N200_..._Dominant — Cue: ...employed or running your own business...
  - N200_..._Influential — Cue: ...are you working for someone or do you run your own business...
  - N200_..._Steady — Cue: ...Take your time to think about it
  - N200_..._Conscientious — Cue: ...I’m interested in understanding your current professional situation
- [ ] Tested — Notes:

## 3. Income & Vehicle Questions

N201A_Employed_AskYearlyIncome_V8_Adaptive
- Goal: Ask current yearly income
- Cue: What's that job producing for you yearly, approximately?
- Transitions: default → N201B_Employed_AskSideHustle_V4_FullyTuned
- [ ] Tested — Notes:

N201B_Employed_AskSideHustle_V4_FullyTuned
- Goal: Ask if side hustle existed in last two years
- Cue: In the last two years, did you have any side hustle...
- Transitions: yes → N201C_Employed_AskSideHustleAmount_V3_FullyTuned; no → N201D_Employed_AskVehicleQ_V5_Adaptive; default → N201D_...
- [ ] Tested — Notes:

N201C_Employed_AskSideHustleAmount_V3_FullyTuned
- Goal: Ask monthly income from side hustle
- Cue: What was that side hustle bringing in on a good month?
- Transitions: default → N201D_Employed_AskVehicleQ_V5_Adaptive
- [ ] Tested — Notes:

N201D_Employed_AskVehicleQ_V5_Adaptive
- Goal: Vehicle question vs current earnings
- Cue: Do you see yourself generating at least {Amount_Reference_Employed}...
- Transitions: affirms_vehicle → Logic_Split_Node_Financial_Qualification; default → Logic_Split_Node_Financial_Qualification
- [ ] Tested — Notes:

N202A_AskCurrentMonthlyRevenue_V7_FullyTuned
- Goal: Ask current monthly revenue (owner)
- Cue: Where's your monthly revenue at right now, roughly?
- Transitions: default → N202B_AskHighestRevenueMonth_V4_FullyTuned
- [ ] Tested — Notes:

N202B_AskHighestRevenueMonth_V4_FullyTuned
- Goal: Ask for highest monthly revenue in last two years
- Cue: What was the highest monthly revenue point?
- Transitions: default → N202C_AskVehicleQuestion_BusinessOwner_V4_Adaptive
- [ ] Tested — Notes:

N202C_AskVehicleQuestion_BusinessOwner_V4_Adaptive
- Goal: Vehicle question vs revenue/profit target
- Cue: ...generate at least {Amount_Reference_Phrase} using this model...
- Transitions: affirms_vehicle → Logic_Split_Node_Financial_Qualification; default → Logic_Split_Node_Financial_Qualification
- [ ] Tested — Notes:

N201E_Unemployed_EmpathyAskPastYearlyIncome_V5_Adaptive
- Goal: Empathize; ask past yearly income
- Cue: I'm sorry to hear that... when you were working, what was that yearly, roughly?
- Transitions: default → N201F_Unemployed_AskSideHustle_V4_FullyTuned
- [ ] Tested — Notes:

N201F_Unemployed_AskSideHustle_V4_FullyTuned
- Goal: Ask about side hustle last two years
- Cue: In the last two years, did you have any side hustle...
- Transitions: yes → N201G_Unemployed_AskSideHustleAmount; no → N201H_Unemployed_AskVehicleQ_V4_FullyTuned; default → N201H_...
- [ ] Tested — Notes:

N201G_Unemployed_AskSideHustleAmount
- Goal: Ask monthly income from side hustle (unemployed)
- Cue: What does that side hustle bring in monthly, roughly?
- Transitions: default → N201H_Unemployed_AskVehicleQ_V4_FullyTuned
- [ ] Tested — Notes:

N201H_Unemployed_AskVehicleQ_V4_FullyTuned
- Goal: Vehicle question vs past earnings with support framing
- Cue: Do you see yourself generating at least [Amount_Reference_Unemployed]...
- Transitions: affirms_vehicle → Logic_Split_Node_Financial_Qualification; default → Logic_Split_Node_Financial_Qualification
- [ ] Tested — Notes:

## 4. Financial Qualification

Logic_Split_Node_Financial_Qualification
- Goal: Route by income level
- Cue: logic split
- Transitions: high_income → N_AskCapital_15k_V1_Adaptive; standard_income → N_AskCapital_5k_Direct_V1_Adaptive
- [ ] Tested — Notes:

N_AskCapital_15k_V1_Adaptive
- Goal: Ask if they have 15–25k liquid
- Cue: ...about fifteen to twenty-five thousand dollars in liquid capital...
- Transitions: has_15_25k → N_ConfirmCommitment_FinalCheck_V1_Adaptive; no_15_25k → N_AskCapital_5k_V1_Adaptive; default → N_AskCapital_5k_V1_Adaptive
- [ ] Tested — Notes:

N_AskCapital_5k_V1_Adaptive
- Goal: Ask if they have 5k minimum
- Cue: The absolute minimum to get started is closer to five thousand...
- Transitions: has_5k → N_ConfirmCommitment_FinalCheck_V1_Adaptive; no_5k → N205C_AskCreditScore_650_V1_FullyTuned; default → N205C_...
- [ ] Tested — Notes:

N_AskCapital_5k_Direct_V1_Adaptive
- Goal: Directly ask for minimum 5k
- Cue: The absolute minimum is around five thousand dollars...
- Transitions: has_5k → N_ConfirmCommitment_FinalCheck_V1_Adaptive; no_5k → N205C_AskCreditScore_650_V1_FullyTuned; default → N205C_...
- [ ] Tested — Notes:

N205C_AskCreditScore_650_V1_FullyTuned
- Goal: Ask if credit score ≥ 650
- Cue: Do you have a credit score of at least six fifty?
- Transitions: score_over_650 → N_ConfirmCommitment_FinalCheck_V1_Adaptive; score_under_650 → Disqualified; default → Disqualified
- [ ] Tested — Notes:

Disqualified
- Goal: Gracefully handle disqualification
- Cue: This might not be the right fit at this time...
- Transitions: default → N_EndCall_Final_V2_Decisive
- [ ] Tested — Notes:

## 5. Motivation & Scheduling Proposal

N_ConfirmCommitment_FinalCheck_V1_Adaptive
- Goal: Secure verbal commitment to attend
- Cue: Aside from emergencies, is there any reason you won't be available...
- Transitions: committed → N401_AskWhyNow_Initial_V10_AssertiveFrame; default → N401_...
- [ ] Tested — Notes:

N401_AskWhyNow_Initial_V10_AssertiveFrame
- Goal: Ask why now; assertive frame
- Cue: Is there a specific reason you're looking to make a change right now...
- Transitions: motivation_provided → N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned; callback_requested → N402_...; default → N402_...
- [ ] Tested — Notes:

N402_Compliment_And_AskYouKnowWhy_V5_FullyTuned
- Goal: Acknowledge; compliment; ask You know why?
- Cue: I appreciate you sharing that... You know why?
- Transitions: callback_requested → N403_IdentityAffirmation_And_ValueFitQuestion_V8_GoalAligned; default → N403_...
- [ ] Tested — Notes:

N403_IdentityAffirmation_And_ValueFitQuestion_V8_GoalAligned
- Goal: Identity affirmation; confirm concept fit
- Cue: ...you’re the type of person that is serious... does this sound like it could fit?
- Transitions: fits → N500A_ProposeDeeperDive_V5_Adaptive; callback_requested → N_Obj_RealBusy_BluntCheck_V3_Adaptive; default → N500A_...
- [ ] Tested — Notes:

N500A_ProposeDeeperDive_V5_Adaptive
- Goal: Propose scheduling a deeper dive call
- Cue: What we need to do is set up another call...
- Transitions: agrees → N500B_AskTimezone_V2_FullyTuned; default → N500B_...
- [ ] Tested — Notes:

N500B_AskTimezone_V2_FullyTuned
- Goal: Ask for timezone
- Cue: What timezone are you in?
- Transitions: default → N_AskForCallbackRange_V1_Adaptive
- [ ] Tested — Notes:

N_AskForCallbackRange_V1_Adaptive
- Goal: Determine available time range
- Cue: When are you typically back at your desk... good time range?
- Transitions: default → N_Scheduling_AskTime_V2_SmartAmbiguity
- [ ] Tested — Notes:

N_Scheduling_AskTime_V2_SmartAmbiguity
- Goal: Ask preferred appointment time; handle AM/PM ambiguity
- Cue: When would be a good time for that call?
- Transitions: default → N_ConfirmVideoCallEnvironment_V1_Adaptive
- [ ] Tested — Notes:

N_ConfirmVideoCallEnvironment_V1_Adaptive
- Goal: Confirm joining Zoom from computer
- Cue: Does that time work to join the video call from your computer?
- Transitions: confirmed → N206_AskAboutPartners_IfFinanciallyQualified; default → N206_...
- [ ] Tested — Notes:

## 6. Scheduling Logistics

N206_AskAboutPartners_IfFinanciallyQualified
- Goal: Ask about other decision-makers
- Cue: Is there anyone else involved, like spouse or partners?
- Transitions: partner → N018_ConfirmPartnerAvailability; no_partner → N_ConfirmCommitment_FinalCheck_V1_Adaptive; default → N_ConfirmCommitment_FinalCheck_V1_Adaptive
- [ ] Tested — Notes:

N018_ConfirmPartnerAvailability
- Goal: Confirm partner availability for chosen time
- Cue: Can {{partner_reference}} be on the call at {{chosen_time_with_ampm}} on {{chosen_day}}?
- Transitions: available → N_ConfirmCommitment_FinalCheck_V1_Adaptive; not_available → N_Scheduling_RescheduleAndHandle_V5_FullyTuned; unsure → N017D_SuggestPartnerCheck_ScheduleFollowUpCall; default → N_ConfirmCommitment_FinalCheck_V1_Adaptive
- [ ] Tested — Notes:

N017D_SuggestPartnerCheck_ScheduleFollowUpCall
- Goal: Get timeframe to check partner; propose follow-up call
- Cue: When’s the soonest you can get in touch to find out... then I’ll give you a quick ring...
- Transitions: default → N_ConfirmCommitment_FinalCheck_V1_Adaptive
- [ ] Tested — Notes:

N_Scheduling_RescheduleAndHandle_V5_FullyTuned
- Goal: Reschedule using objection toolkit
- Cue: reschedule handling based on webhook unavailability
- Transitions: new_time_found → N_ConfirmCommitment_FinalCheck_V1_Adaptive; default → N_ConfirmCommitment_FinalCheck_V1_Adaptive
- [ ] Tested — Notes:

## 7. Final Confirmation & Close

N_AskAboutReminderSetup_V1_Adaptive
- Goal: Ask if they know how to set phone reminder
- Cue: Do you know how to set up a reminder on your phone?
- Transitions: default → N_CheckForTextReceipt_V1_Adaptive
- [ ] Tested — Notes:

N_CheckForTextReceipt_V1_Adaptive
- Goal: Confirm receipt of confirmation text
- Cue: Did that come through on your end yet?
- Transitions: received → N_ConfirmAndRequestReply_V4_PatientListener; default → N_ConfirmAndRequestReply_V4_PatientListener
- [ ] Tested — Notes:

N_ConfirmAndRequestReply_V4_PatientListener
- Goal: Get text reply “Confirmed, I’ll see you there” now
- Cue: Respond to that message with Confirmed, I’ll see you there...
- Transitions: default → N_Video_Assign_GentleIntro_V3_FullyTuned
- [ ] Tested — Notes:

N_Video_Assign_GentleIntro_V3_FullyTuned
- Goal: Introduce 12-minute overview; secure agreement to watch
- Cue: There’s a short 12-minute video... are you able to give that a quick watch?
- Transitions: agrees → N_Video_ReinforceValue_FeeContext_V3_FullyTuned; default → N_Video_ReinforceValue_FeeContext_V3_FullyTuned
- [ ] Tested — Notes:

N_Video_ReinforceValue_FeeContext_V3_FullyTuned
- Goal: Reinforce value; fee waived context
- Cue: Kendrick’s time is usually set at a thousand dollars... fee is waived...
- Transitions: default → N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint
- [ ] Tested — Notes:

N_Video_RelateSocialProof_Part2_LogicHook_V3_Checkpoint
- Goal: Provide logical reason why video is essential
- Cue: That 12-minute video makes sure you’re fully in the loop...
- Transitions: logic_acknowledged → N_Video_AssignAndCommit_V1_FullyTuned; default → N_Video_AssignAndCommit_V1_FullyTuned
- [ ] Tested — Notes:

N_Video_AssignAndCommit_V1_FullyTuned
- Goal: Secure direct commitment to watch immediately after call
- Cue: If I send you that video right after we hang up, can you watch now?
- Transitions: commits → N_Video_ConfirmAndReply_V1_Adaptive; default → N_Video_ConfirmAndReply_V1_Adaptive
- [ ] Tested — Notes:

N_Video_ConfirmAndReply_V1_Adaptive
- Goal: Get “Got it” reply to video link now
- Cue: I’m sending that link now. Reply Got it so I know you received it.
- Transitions: default → N_Finalize_And_EndCall_V1_Adaptive
- [ ] Tested — Notes:

N_Finalize_And_EndCall_V1_Adaptive
- Goal: Deliver final instruction about reply to avoid cancellation; warm close
- Cue: The last and most important step is to reply to that text...
- Transitions: default → N_EndCall_Final_V2_Decisive
- [ ] Tested — Notes:

N_EndCall_Final_V2_Decisive
- Goal: Final professional closing; terminate call
- Cue: You are all set... Have a great rest of your day. Goodbye.
- Transitions: default → EndCall
- [ ] Tested — Notes:

## 8. Dismissal & Busy Loops

N003B_DeframeInitialObjection_V7_GoalOriented
- Goal: De-frame initial objection; elicit curiosity/interest
- Cue: Many people feel that way... what if it were possible...
- Transitions: default → N_IntroduceModel_And_AskQuestions_V3_Adaptive
- [ ] Tested — Notes:

N003_NoRecall_PivotAndChallenge_V18_FullyTuned
- Goal: Pivot from no ad recall; test interest; challenge disinterest
- Cue: Are you focused on creating new income streams right now?
- Transitions: callback_requested → N_Obj_RealBusy_BluntCheck_V3_Adaptive; shows_interest → N_IntroduceModel_...; default → N_IntroduceModel_...
- [ ] Tested — Notes:

N_Obj_EarlyDismiss_AskShareBackground_V7
- Goal: Acknowledge skepticism; request 20s to share background
- Cue: I was skeptical too... Do you mind if I take 20 seconds...
- Transitions: agrees → N_Obj_EarlyDismiss_ShareBackground_DeliverStoryHook_V3_FullyTuned; declines → N_Obj_EarlyDismiss_DirectValueChallenge_V9_EscalationEnabled; default → N_Obj_EarlyDismiss_ShareBackground_DeliverStoryHook_V3_FullyTuned
- [ ] Tested — Notes:

N_Obj_EarlyDismiss_ShareBackground_DeliverStoryHook_V3_FullyTuned
- Goal: Share background; state income potential; ask hook
- Cue: I’m a military veteran... seen firsthand it’s possible to pull in an extra 20,000...
- Transitions: default → N_Obj_EarlyDismiss_ShareBackgroundAskWhy
- [ ] Tested — Notes:

N_Obj_EarlyDismiss_ShareBackgroundAskWhy
- Goal: Share background and ask if they know why opportunity is good
- Cue: ...this has given people... real shot at an extra 20,000... Do you know why?
- Transitions: default → N_Obj_EarlyDismiss_ExplainReasonAndExplore
- [ ] Tested — Notes:

N_Obj_EarlyDismiss_ExplainReasonAndExplore
- Goal: Edify value; ask if it’s interesting
- Cue: Because thousands of students already generated over 20,000 per month... worth exploring?
- Transitions: still_interested → N_IntroduceModel_And_AskQuestions_V3_Adaptive; default → N_IntroduceModel_...
- [ ] Tested — Notes:

N_Obj_EarlyDismiss_DirectValueChallenge_V9_EscalationEnabled
- Goal: Direct value hook to reignite curiosity
- Cue: If I shared a real shot at an extra 20,000 a month passively...
- Transitions: still_interested → N_Obj_EarlyDismiss_ConnectToCurrentCall_V5_LeadOut; default → N_Obj_EarlyDismiss_ConnectToCurrentCall_V5_LeadOut
- [ ] Tested — Notes:

N_Obj_EarlyDismiss_ConnectToCurrentCall_V5_LeadOut
- Goal: Confirm call is about income potential; ask if worth exploring
- Cue: That’s exactly what the next couple of minutes are about...
- Transitions: exploration_agreed → N_IntroduceModel_And_AskQuestions_V3_Adaptive; default → N_IntroduceModel_...
- [ ] Tested — Notes:

N_Obj_RealBusy_BluntCheck_V3_Adaptive
- Goal: Diagnose time constraint vs value skepticism
- Cue: Let me be blunt... not sure why listening, or a meeting coming up?
- Transitions: meeting_coming_up → N_Obj_RealBusy_AskMeetingTime; not_sure_why_listening → N_Obj_RealBusy_OfferReschedule; default → N_Obj_RealBusy_OfferReschedule
- [ ] Tested — Notes:

N_Obj_RealBusy_AskMeetingTime
- Goal: Ask how long until their meeting
- Cue: In how long is your meeting?
- Transitions: time_given → N_Obj_RealBusy_StateRemainingTimeAndWrapUp; vague → N_Obj_RealBusy_OfferReschedule; default → N_Obj_RealBusy_OfferReschedule
- [ ] Tested — Notes:

N_Obj_RealBusy_StateRemainingTimeAndWrapUp
- Goal: State remaining time; signal quick wrap-up
- Cue: That means we have about [remaining time]... Let me wrap this up...
- Transitions: default → N_Opener_StackingIncomeHook_V3_CreativeTactic
- [ ] Tested — Notes:

N_Obj_RealBusy_OfferReschedule
- Goal: Ask for better time later
- Cue: When will be a better time to talk later?
- Transitions: default → N_Obj_RealBusy_ConfirmRescheduleTime
- [ ] Tested — Notes:

N_Obj_RealBusy_ConfirmRescheduleTime
- Goal: Reiterate exact reschedule time; ask for 100% confirmation
- Cue: So you will be 100% available at [exact time]?
- Transitions: confirmed → N_Obj_RealBusy_StateCallbackAndTeaseGuarantees; default → N_Obj_RealBusy_StateCallbackAndTeaseGuarantees
- [ ] Tested — Notes:

N_Obj_RealBusy_StateCallbackAndTeaseGuarantees
- Goal: Confirm callback time; tease 3 guarantees; gauge worth exploring
- Cue: I’ll call you back at [time]... we have 3 guarantees... An ROI guarantee...
- Transitions: worth_exploring → N_ConfirmCommitment_FinalCheck_V1_Adaptive; default → N_ConfirmCommitment_FinalCheck_V1_Adaptive
- [ ] Tested — Notes:

## End of Flow

N_EndCall_Final_V2_Decisive
- Goal: Final professional close; send confirmation email; end call
- Cue: You are all set... confirmation email... Goodbye.
- Transitions: default → EndCall
- [ ] Tested — Notes:

Acceptance reminder for success path
- Booking confirmed: confirmation text replied “Confirmed, I’ll see you there”
- Homework video commitment: explicit commitment to watch and “Got it” reply to video link