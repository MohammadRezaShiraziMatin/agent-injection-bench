# AIB P4.2.3 — Harness / Adapter Coverage Audit

**Gate:** Read-only audit (no dataset mutation, no live LLM, no AdaptiGuard evaluation).
**Baseline:** branch `cursor/p4-2-dataset-6db2`, HEAD `1c4624f`, HR audit **200/200**, P4.2 digest `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee`.

## 1. Harness reference (implementation evidence)

**Primary execution path:** `agent/loop.py` (`run_episode`).

| Surface | Present in episode JSON | Consumed in harness prompt / loop | Evidence |
|---------|----------------------|-----------------------------------|----------|
| `user_query` | Yes | **Yes** | `user_task = episode["user_query"]`; user message block |
| `retrieved_docs` | Optional | **Yes** | `_docs_block(episode)` appended to user message |
| `tool_results` | Optional | **No** | Not read; tools invoked only via LLM `tool_calls` → `call_tool(..., docs=docs)` |
| `conversation` | Optional | **No** | No replay of `conversation[]` |
| `memory_store` | Optional | **No** | Not referenced |
| `session_state` | Optional | **No** | Not referenced |
| `cross_context` | Optional | **No** | Not referenced |
| `inter_agent_messages` | Optional | **No** | No multi-agent bus |
| `adaptive_trace` | Optional | **No** | No feedback-loop driver |

**Tools:** mock `search_docs`, `send_email` via `agent/tools.py` (proposal vs execution observable in trace; scoring separate).

**Defenses:** none in harness (`agent/__init__.py`: “no defenses”).

Classification rule (this audit): compare **attack-relevant injection surfaces** (from `injection.locus` + family) to harness-consumed set `{user_query, retrieved_docs}`. Multi-agent / adaptive families require mechanisms **absent** from `loop.py` → `DESIGNED_NOT_EXECUTABLE`.

## 2. Dataset coverage (200 episodes)

Counts from per-episode `execution.executability` (authored against the same harness reference; cross-checked against `loop.py` rules below).

| Status | All 200 | Attack (100) | Benign (100) |
|--------|--------:|-------------:|-------------:|
| **EXECUTABLE** | 68 | 34 | 34 |
| **PARTIALLY_EXECUTABLE** | 116 | 58 | 58 |
| **DESIGNED_NOT_EXECUTABLE** | 16 | 8 | 8 |

Pair-level: benign twins share executability label with attack twin (by design).

### Harness-derived attack classification (implementation)

| Family | Attacks | Status | Reason (harness) |
|--------|--------:|--------|------------------|
| `direct_prompt_injection` | 10 | EXECUTABLE | Injection via `user_query` in prompt |
| `indirect_prompt_injection` | 8 | EXECUTABLE | Injection via `retrieved_docs` in prompt |
| `rag_document_injection` | 16 | EXECUTABLE | Injection via `retrieved_docs` |
| `web_retrieved_content_injection` | 10 | PARTIALLY_EXECUTABLE | Content in `retrieved_docs`; no separate web/crawl surface (`execution.missing_adapter_note`) |
| `tool_output_injection` | 14 | PARTIALLY_EXECUTABLE | `tool_results` not injected into prompt |
| `multi_turn_injection` | 12 | PARTIALLY_EXECUTABLE | `conversation` not replayed |
| `memory_state_injection` | 12 | PARTIALLY_EXECUTABLE | `memory_store` / `session_state` not loaded |
| `cross_context_injection` | 10 | PARTIALLY_EXECUTABLE | `cross_context` not injected |
| `multi_agent_injection` | 4 | DESIGNED_NOT_EXECUTABLE | No `inter_agent_messages` path |
| `adaptive_injection` | 4 | DESIGNED_NOT_EXECUTABLE | No `adaptive_trace` loop |

Matches `docs/AIB_P4_2_EXECUTABILITY_MATRIX.md` attack summary (34 / 58 / 8).

## 3. Surface coverage summary

| Surface | Dataset (attacks using) | Harness consumed | Audit status |
|---------|----------------------:|------------------|--------------|
| `user_query` | 10 direct | Yes | EXECUTABLE for direct family |
| `retrieved_docs` | 44+ (indirect/RAG/web) | Yes | EXECUTABLE / PARTIAL (web) |
| `tool_results` | 14 | No | PARTIAL |
| `conversation` | 12 multi-turn | No | PARTIAL |
| `memory_store` / `session_state` | 12 | No | PARTIAL |
| `cross_context` | 10 | No | PARTIAL |
| `inter_agent_messages` | 4 | No | NOT EXECUTABLE |
| `adaptive_trace` | 4 | No | NOT EXECUTABLE |

## 4. D0 / D1 / D2 / AdaptiGuard

| Layer | Implemented in this repo? | Coverage | Gaps |
|-------|---------------------------|----------|------|
| **D0** (baseline harness, no defense) | **Yes** — `agent/loop.py` | Episodes whose attack surfaces ⊆ `{user_query, retrieved_docs}` prompt path (**34** attacks / **68** with benign twins) | Does not surface tool_results, conversation, memory, cross_context, multi-agent, adaptive |
| **D1** | **CONTRACT_ONLY** | Documented in benchmark/dataset cards as external evaluation layer; **no D1 adapter module** in tree | Input mapping, defense hooks not implemented here |
| **D2** | **CONTRACT_ONLY** | Same; `docs/ADAPTI_GUARD_BRIDGE.md` describes **external** defense repo integration | No in-repo D2 runner |
| **AdaptiGuard** | **Not integrated** | Bridge checklist only (`docs/ADAPTI_GUARD_BRIDGE.md`); no `AIB episode → D2 adapter → AdaptiGuard → result` code path | Full input/output mapping **unsupported** in this repository |

**P7 protocol docs:** Referenced in `docs/AIB_P4_2_BENCHMARK_CARD.md` (`AIB_P7_EVALUATION_PROTOCOL.md`, `AIB_P7_LIVE_EVAL_GATE.md`) but **not present** on this branch → live-eval gate rules **NOT VERIFIED** in-tree.

## 5. Scientific distinctions (preserved)

| Concept | P4.2.3 finding |
|---------|----------------|
| Dataset-designed | 200 episodes encode diverse surfaces (including non-harness fields) |
| Harness-consumable | Only `user_query` + `retrieved_docs` enter `loop.py` today |
| Actually-executable | 68 episodes fully aligned; 116 partial; 16 designed-not-executable under v0 |
| Live-evaluated | **Not performed** in this gate |
| S2 vs S3/S4 | Episodes use **S2** proposal criteria; harness mock tools do not imply external side effects |

## 6. Required adapter surfaces (future work — not implemented)

From `docs/AIB_P4_2_EXECUTABILITY_MATRIX.md` (unchanged by this audit):

- `conversation` replay (multi-turn, and related)
- `tool_results` pre-seeding
- `memory_store` / `session_state` blocks
- `cross_context` auxiliary channels
- `multi_agent_channel`
- `adaptive_loop`

## 7. Integrity & tests (this gate)

| Check | Result |
|-------|--------|
| P4.2 digest | Unchanged `4b2e6f59…` |
| P4.1 / v0 | `verify_p6_freeze.py` PASS; no episode edits |
| `qc_p4_2.py` | PASS (200/200, leakage, reproducibility) |
| `pytest` | **38 passed** (full suite) |
| HR audit | **200** decisions (unchanged) |
| Live LLM / AdaptiGuard | **Not run** |

## 8. Gate outcome

**PASS** — All **200** P4.2 episodes accounted for; executability aligned with **`agent/loop.py`** implementation and existing executability matrix; D1/D2/AdaptiGuard documented as contract-only / external; dataset immutable.

## 9. Next gate (repository evidence; not executed)

- **P4.2 dataset freeze / P6-style pin** — not authorized in P4.2.2 workflow until harness adapters close documented gaps (optional human policy).
- **P7 live evaluation** — requires in-tree or pinned P7 protocol + model lock (`AIB_P4_2_BENCHMARK_CARD.md`); docs absent on this branch.
- **Harness adapter implementation** — engineering follow-up to raise PARTIAL/DNE cohorts toward truthful execution (separate from this audit).

---

*Episode-level rows: `data/episodes_p4_2/*/atk_p42_*.json` fields `execution.executability`, `execution.harness_surfaces`, `execution.missing_adapter_note`.*
