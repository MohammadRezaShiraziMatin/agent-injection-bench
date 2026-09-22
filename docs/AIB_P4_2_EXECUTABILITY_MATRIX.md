# AIB P4.2 Executability Matrix

Harness reference: `agent/loop.py` (system prompt + `user_query` + `retrieved_docs` only; mock tools `search_docs`, `send_email`).

## Summary counts (attack episodes)

| Status | Count |
|--------|------:|
| EXECUTABLE | 34 |
| PARTIALLY_EXECUTABLE | 58 |
| DESIGNED_NOT_EXECUTABLE | 8 |

## By family

| Family | Pairs | Dataset surfaces | Harness today | Status |
|--------|------:|------------------|---------------|--------|
| `direct_prompt_injection` | 10 | `user_query`, `retrieved_docs` | Injected into prompt | EXECUTABLE |
| `indirect_prompt_injection` | 8 | `retrieved_docs` | Injected into prompt | EXECUTABLE |
| `rag_document_injection` | 16 | `retrieved_docs` | Injected into prompt | EXECUTABLE |
| `web_retrieved_content_injection` | 10 | `retrieved_docs` (+ `source_kind`) | Treated as docs; no web crawler | PARTIALLY_EXECUTABLE |
| `tool_output_injection` | 14 | `tool_results` | **Not** passed to LLM | PARTIALLY_EXECUTABLE |
| `multi_turn_injection` | 12 | `conversation` | **Not** replayed | PARTIALLY_EXECUTABLE |
| `memory_state_injection` | 12 | `memory_store`, `session_state` | **Not** loaded | PARTIALLY_EXECUTABLE |
| `cross_context_injection` | 10 | `cross_context` | **Not** injected | PARTIALLY_EXECUTABLE |
| `multi_agent_injection` | 4 | `inter_agent_messages` | No multi-agent bus | DESIGNED_NOT_EXECUTABLE |
| `adaptive_injection` | 4 | `adaptive_trace` | No feedback loop | DESIGNED_NOT_EXECUTABLE |

## Required future adapter surfaces

| Surface | Episodes using (attack) | Gap |
|---------|-------------------------|-----|
| `conversation` | 12 multi-turn + 4 multi-agent + 4 adaptive | Replay prior turns before final user message |
| `tool_results` | 14 | Pre-seed tool output in prompt or simulated prior step |
| `memory_store` / `session_state` | 12 | Inject state block with trust boundaries |
| `cross_context` | 10 | Merge auxiliary channels with explicit labels |
| `multi_agent_channel` | 4 | Route inter-agent messages |
| `adaptive_loop` | 4 | Execute scripted or live attempt/observation cycles |

## Per-episode field

Each episode includes `execution.executability`, `execution.harness_surfaces`, and optional `execution.missing_adapter_note`.

Classification rule: **EXECUTABLE** only if all attack-relevant surfaces are represented in the current harness prompt path; otherwise **PARTIALLY_EXECUTABLE** or **DESIGNED_NOT_EXECUTABLE**.
