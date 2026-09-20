# AIB P4.2.2 Human Review Package

> **Automated pre-review only.** Actual human scientific adjudication has not yet occurred. Episode `review_status` remains `unreviewed`.

## Section 1 — Instructions

1. Open `artifacts/p4_2_2_human_review_matrix.json` (or CSV).
2. For each episode, read the attack/benign JSON under `data/episodes_p4_2/`.
3. Record decisions in the `human_decision`, `human_reviewer`, `review_date`, and `human_notes` fields (initially null).
4. Use P4.2.1 near-duplicate adjudication (`artifacts/p4_2_1_near_duplicate_adjudication.json`) when reviewing pairs `p42_083`–`p42_100`.
5. Do not treat n-gram similarity as duplication without mechanism review.

## Section 2 — Decision labels

- **ACCEPT** — Suitable for candidate benchmark after any noted metadata fixes.
- **REVISE** — Specific correction required before freeze.
- **REJECT** — Remove or redesign.
- **UNCERTAIN** — Escalate / second reviewer.

## Section 3 — Reviewer criteria

Evaluate: injection validity, taxonomy, mechanism, objective, target, source, context, horizon, success criterion (S0–S4), pair quality, realism, executability.

## Section 4 — Episode review matrix (200 episodes)

| episode_id | split | family | status | priority | action | exec | dup_risk |
|---|---|---|---|---|---|---|---|
| atk_p42_001 | attack | direct_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_002 | attack | direct_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_003 | attack | direct_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_004 | attack | direct_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_005 | attack | direct_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_006 | attack | direct_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_007 | attack | direct_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_008 | attack | direct_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_009 | attack | direct_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_010 | attack | direct_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_011 | attack | indirect_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_012 | attack | indirect_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_013 | attack | indirect_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_014 | attack | indirect_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_015 | attack | indirect_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_016 | attack | indirect_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_017 | attack | indirect_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_018 | attack | indirect_prompt_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_019 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_020 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_021 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_022 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_023 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_024 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_025 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_026 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_027 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_028 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_029 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_030 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_031 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_032 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_033 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_034 | attack | rag_document_injection | ACCEPT_CANDIDATE | P2 | KEEP | EXECUTABLE | LOW |
| atk_p42_035 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_036 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_037 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_038 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_039 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_040 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_041 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_042 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_043 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_044 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_045 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_046 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_047 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_048 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_049 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_050 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_051 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_052 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_053 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_054 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_055 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_056 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_057 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_058 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_059 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_060 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_061 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_062 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_063 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_064 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_065 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_066 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_067 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_068 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_069 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_070 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_071 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_072 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_073 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_074 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_075 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_076 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_077 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_078 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_079 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_080 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_081 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_082 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_083 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_084 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_085 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_086 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_087 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_088 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_089 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_090 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_091 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_092 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_093 | attack | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_094 | attack | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_095 | attack | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_096 | attack | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_097 | attack | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_098 | attack | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_099 | attack | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_100 | attack | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_001 | benign | direct_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_002 | benign | direct_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_003 | benign | direct_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_004 | benign | direct_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_005 | benign | direct_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_006 | benign | direct_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_007 | benign | direct_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_008 | benign | direct_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_009 | benign | direct_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_010 | benign | direct_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_011 | benign | indirect_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_012 | benign | indirect_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_013 | benign | indirect_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_014 | benign | indirect_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_015 | benign | indirect_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_016 | benign | indirect_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_017 | benign | indirect_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_018 | benign | indirect_prompt_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_019 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_020 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_021 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_022 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_023 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_024 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_025 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_026 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_027 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_028 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_029 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_030 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_031 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_032 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_033 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_034 | benign | rag_document_injection | ACCEPT_CANDIDATE | P3 | KEEP | EXECUTABLE | LOW |
| ben_p42_035 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_036 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_037 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_038 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_039 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_040 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_041 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_042 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_043 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_044 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_045 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_046 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_047 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_048 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_049 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_050 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_051 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_052 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_053 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_054 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_055 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_056 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_057 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_058 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_059 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_060 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_061 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_062 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_063 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_064 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_065 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_066 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_067 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_068 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_069 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_070 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_071 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_072 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_073 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_074 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_075 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_076 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_077 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_078 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_079 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_080 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_081 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_082 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_083 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_084 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_085 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_086 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_087 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_088 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_089 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_090 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_091 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_092 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_093 | benign | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_094 | benign | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_095 | benign | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_096 | benign | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_097 | benign | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_098 | benign | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_099 | benign | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_100 | benign | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |

## Section 5 — Priority review queue

Episodes with P1 priority, UNCERTAIN status, partial/non-executable harness surfaces, or near-duplicate cluster membership (132 rows):

| episode_id | split | family | status | priority | action | exec | dup_risk |
|---|---|---|---|---|---|---|---|
| atk_p42_035 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_036 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_037 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_038 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_039 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_040 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_041 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_042 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_043 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_044 | attack | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_045 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_046 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_047 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_048 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_049 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_050 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_051 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_052 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_053 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_054 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_055 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_056 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_057 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_058 | attack | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_059 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_060 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_061 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_062 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_063 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_064 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_065 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_066 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_067 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_068 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_069 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_070 | attack | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_071 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_072 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_073 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_074 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_075 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_076 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_077 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_078 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_079 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_080 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_081 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_082 | attack | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| atk_p42_083 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_084 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_085 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_086 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_087 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_088 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_089 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_090 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_091 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_092 | attack | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| atk_p42_093 | attack | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_094 | attack | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_095 | attack | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_096 | attack | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_097 | attack | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_098 | attack | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_099 | attack | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| atk_p42_100 | attack | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_035 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_036 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_037 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_038 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_039 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_040 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_041 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_042 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_043 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_044 | benign | web_retrieved_content_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_045 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_046 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_047 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_048 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_049 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_050 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_051 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_052 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_053 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_054 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_055 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_056 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_057 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_058 | benign | tool_output_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_059 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_060 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_061 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_062 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_063 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_064 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_065 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_066 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_067 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_068 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_069 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_070 | benign | multi_turn_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_071 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_072 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_073 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_074 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_075 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_076 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_077 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_078 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_079 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_080 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_081 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_082 | benign | memory_state_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | LOW |
| ben_p42_083 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_084 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_085 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_086 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_087 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_088 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_089 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_090 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_091 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_092 | benign | cross_context_injection | ACCEPT_CANDIDATE | P1 | REVIEW_HUMAN | PARTIALLY_EXECUTABLE | MEDIUM |
| ben_p42_093 | benign | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_094 | benign | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_095 | benign | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_096 | benign | multi_agent_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_097 | benign | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_098 | benign | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_099 | benign | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |
| ben_p42_100 | benign | adaptive_injection | UNCERTAIN_HUMAN_REQUIRED | P1 | REVIEW_HUMAN | DESIGNED_NOT_EXECUTABLE | MEDIUM |

### Near-duplicate cluster (P4.2.1)

- 114 ordered n-gram flags among attack episodes `atk_p42_083`–`atk_p42_100`
- P4.2.1 adjudication: **VALID_VARIANT** (keep both)
- **Human confirmation recommended:** 36 episodes (pairs `p42_083`–`p42_100`)

## Section 6 — Reviewer decision fields

For each episode in the matrix JSON:

```text
human_decision:
human_reviewer:
review_date:
human_notes:
```

(All null until a human reviewer completes adjudication.)
