# AIB P4.1 Dataset Plan

**Status:** Controlled reconstruction (not historical P4 recovery)  
**Dataset version:** `P4.1`  
**Schema:** `schema/episode.v1.json` (additive; `schema/episode.schema.json` / v0 unchanged)

---

## 0. Repository context

### Baseline verified (Phase 0)

| Item | Value |
|------|--------|
| `HEAD` | `6bced24ea34b9325d3d983ead6ff967d469d1378` |
| Branch | `main` |
| v0 episodes | **42** (`validate_episodes.py`: **0 errors**) |
| Pre-P4.1 pytest | **14** tests |

### Missing upstream docs (fact, not invented)

This checkout does **not** contain separate P2 / P2.5 / P3 markdown artifacts or a pre-existing `episode.v1.json` in git history. P4.1 therefore defines the **candidate v1 schema and enums in-repo** (`schema/episode.v1.json`), aligned with:

- Frozen v0 harness fields (`user_query`, `retrieved_docs`, `injection`, `expected`)
- Publication-branch pattern techniques (`docs/TAXONOMY.md` on `origin/publication/phase-c-publication`, read via `git show` — not merged into `main`)
- Explicit P4.1 task family list (RAG, tool-output, multi-turn, cross-context, state-dependent, memory poisoning)

**P4.1 IS A NEW CONTROLLED RECONSTRUCTION, NOT RECOVERY OF HISTORICAL P4 ARTIFACTS.**

---

## 1. Objectives

1. Add **20 new** candidate episodes (**10 attack + 10 benign**) under `data/episodes_v1/`.
2. Cover six injection **families** with synthetic campus-admin scenarios **not duplicated from v0** `user_query` text.
3. Provide deterministic regeneration (`scripts/gen_p4_1_dataset.py`, seed `41020260920`).
4. Mark all episodes `provenance.review_status = unreviewed`, `provenance.reconstruction = P4.1`.
5. Leave `data/episodes/` byte-identical.

---

## 2. Layout

```
data/episodes_v1/
  attack/atk_p41_01.json … atk_p41_10.json
  benign/ben_p41_01.json … ben_p41_10.json
  MANIFEST.json
scripts/gen_p4_1_dataset.py
scripts/qc_p4_1.py
schema/episode.v1.json
```

IDs: `atk_p41_NN` / `ben_p41_NN`; pairs: `pair_id = p41_NN`.

---

## 3. Taxonomy (frozen enums in `episode.v1.json`)

| Dimension | Values (subset) |
|-----------|------------------|
| **family** | `rag_document_injection`, `tool_output_injection`, `multi_turn_injection`, `cross_context_injection`, `state_dependent_injection`, `memory_poisoning` |
| **technique** | `instruction_override`, `tool_hijack`, `data_disclosure`, `workflow_hijack`, `fake_authorization`, `urgency_social` |
| **objective** | includes `unauthorized_state_change` for memory poisoning |
| **source** | `retrieved_document`, `tool_output`, `prior_turn`, `auxiliary_context`, `session_state`, `memory_store` |
| **target** | `send_email`, `search_docs`, `agent_memory`, `user_response` |
| **path** | `indirect`, `direct_tool_channel`, `cross_boundary`, `state_gated` |
| **interaction_type** | `single_turn`, `multi_turn` |
| **horizon** | `h0`, `h1`, `h2` |
| **context_type** | campus finance/research/IT/HR/facilities/compliance |
| **tool** | `send_email`, `search_docs`, `none` |
| **memory_state** | `none`, `read`, `write`, `poisoned` |

**Memory poisoning:** `taxonomy.objective = unauthorized_state_change` plus required `taxonomy.objective_note` (no new enum).

**Success criterion (expected):** `S0` benign; attacks labeled `S2` unless otherwise noted (proposal vs execution distinguished in metadata — harness does not assert model outcomes).

---

## 4. Planned episode map

| pair_id | family | interaction | horizon | Primary source channel |
|---------|--------|-------------|---------|-------------------------|
| p41_01 | rag_document | single_turn | h0 | retrieved_document |
| p41_02 | rag_document | single_turn | h0 | retrieved_document |
| p41_03 | tool_output | single_turn | h0 | tool_output |
| p41_04 | multi_turn | multi_turn | h1 | prior_turn + document |
| p41_05 | multi_turn | multi_turn | h2 | retrieved_document |
| p41_06 | cross_context | single_turn | h0 | auxiliary_context |
| p41_07 | state_dependent | single_turn | h0 | session_state + document |
| p41_08 | memory_poisoning | single_turn | h0 | memory_store |
| p41_09 | tool_output | single_turn | h0 | tool_output |
| p41_10 | cross_context | single_turn | h0 | auxiliary_context |

Each row is a matched attack/benign pair (`pair_id`).

---

## 5. Non-goals

- No live LLM generation or evaluation
- No AdaptiGuard / defense coupling
- No historical provenance claims
- No edits to v0 episodes or v0 schema
- No P5 human QA in this phase

---

## 6. QC & tests

- `scripts/qc_p4_1.py`: schema, composition, pairing, v0 query collision, duplicates, reproducibility
- `tests/test_p4_1_dataset.py`: v0 byte hashes, v0 validation, P4.1 schema, QC, generator determinism
- Semantic near-duplicates: **NOT_VERIFIED** offline (explicit in QC report)

---

## 7. Gate criteria

- **PASS:** 20 files, QC `ok`, byte-identical regen, v0 preserved, tests green
- **PASS WITH CONDITIONS:** semantic near-dup not verified; human review pending
- **BLOCKED:** QC failures or v0 drift
