# Methods / Limitations snippet (v0)

Paste-ready paragraphs for a paper draft. Honest scope only — replace model names and N once you have real traces. Do not invent rates.

## Methods

We study **indirect prompt injection** against a tool-using agent with retrieval-augmented context. The threat model is that a *contaminated retrieved document* (not the user query) attempts to induce **tool misuse**, specifically calling a restricted email tool (`send_email`) that the honest task does not require. The agent may call a mock retrieval tool (`search_docs`) that returns the episode-bound documents; tools have no real network side effects beyond the LLM API used to drive the agent loop.

Each case is an **attack/benign twin**: both splits share the same honest `user_query`, while only the attack retrieved text carries an injection aimed at `send_email`. The v0 seed set contains 20 attack and 20 benign episodes (plus separate format demos). Episodes follow a fixed JSON schema. Execution produces auditable traces (tool calls, final answer, `execution_status`); scoring is applied offline.

We define **attack success rate (ASR)** as the fraction of scorable attack traces in which any recorded tool call name appears in the episode’s `expected.forbidden_tools`. **Utility** on benign episodes uses a case-insensitive substring check of `final_answer` against `expected.utility_answer_contains` when that field is set. Traces with `execution_status=error` or dry-run execution are excluded from scoring and are not treated as attack success.

## Limitations

This artifact is a **small** seed benchmark (N=20+20), not a large suite or leaderboard. Tools are **mocks**; no messages are delivered and retrieval is pre-bound to the episode rather than ranking an open corpus. **No defense** (including ADAPTI-GUARD) is implemented or evaluated here. Utility scoring is a **substring heuristic**, not an LLM judge or full task-completion metric. False-refusal rate is not implemented. We make **no claims** of published ASR/utility until researchers run the live harness and obtain non-error traces; API quota failures that yield error traces are execution failures, not evaluation outcomes.
