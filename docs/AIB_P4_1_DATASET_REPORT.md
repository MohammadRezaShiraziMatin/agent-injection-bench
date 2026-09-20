# AIB P4.1 Dataset Report

**P4.1 IS A NEW CONTROLLED RECONSTRUCTION, NOT RECOVERY OF HISTORICAL P4 ARTIFACTS.**

---

## 1. Baseline

| Item | Verified value |
|------|----------------|
| `HEAD` (unchanged) | `6bced24ea34b9325d3d983ead6ff967d469d1378` |
| Branch | `main` |
| v0 validation | `n=42`, `errors=0`, `ok=true` |
| v0 `data/episodes/` git diff | **0 bytes** |
| v0 file integrity | `tests/fixtures/v0_episode_sha256.json` (42 files) |
| Pre-P4.1 pytest | 14 tests |
| Post-P4.1 pytest | **20 passed** (6 additive tests) |

No live LLM/API calls. No AdaptiGuard evaluation.

---

## 2. Generated artifacts (additive)

| Artifact | Path |
|----------|------|
| Episodes | `data/episodes_v1/attack/*.json`, `data/episodes_v1/benign/*.json` |
| Manifest | `data/episodes_v1/MANIFEST.json` |
| Schema | `schema/episode.v1.json` |
| Generator | `scripts/gen_p4_1_dataset.py` (seed `41020260920`) |
| QC | `scripts/qc_p4_1.py` |
| Plan | `docs/AIB_P4_1_DATASET_PLAN.md` |
| Tests | `tests/test_p4_1_dataset.py`, `tests/fixtures/v0_episode_sha256.json` |

---

## 3. Composition

| Metric | Count |
|--------|------:|
| Total JSON episodes | **20** |
| Attack | **10** |
| Benign | **10** |
| Matched pairs (`pair_id`) | **10** (`p41_01` … `p41_10`) |
| Unmatched pairs | **0** |

**Episode IDs:** `atk_p41_01`–`atk_p41_10`, `ben_p41_01`–`ben_p41_10`.

---

## 4. Family coverage (attack episodes)

| family | count |
|--------|------:|
| `rag_document_injection` | 2 |
| `tool_output_injection` | 2 |
| `multi_turn_injection` | 2 |
| `cross_context_injection` | 2 |
| `state_dependent_injection` | 1 |
| `memory_poisoning` | 1 |

All six required families appear at least once.

---

## 5. Other taxonomy distributions (attack)

| Dimension | Distribution |
|-----------|--------------|
| **source** | retrieved_document×3, tool_output×2, prior_turn×1, auxiliary_context×2, session_state×1, memory_store×1 |
| **target** | send_email×9, agent_memory×1 |
| **interaction_type** | single_turn×8, multi_turn×2 |
| **horizon** | h0×8, h1×1, h2×1 |
| **context_type** | campus_hr×1, compliance×2, facilities×2, finance×1, it×2, research×2 |
| **tool** | send_email×9, none×1 |
| **memory_state** | none×8, read×1, poisoned×1 |
| **objective** | unauthorized_tool_proposal×5, unauthorized_tool_execution×2, instruction_deviation×1, unauthorized_state_change×1, data_exfiltration×1 |

Memory poisoning episode (`atk_p41_08`) uses `objective=unauthorized_state_change` with `objective_note` (schema-enforced).

---

## 6. Provenance (all episodes)

| Field | Value |
|-------|--------|
| `source_type` | `synthetic` |
| `creation_method` | `deterministic_generator_p4_1` |
| `human_authored` | `false` |
| `synthetic` | `true` |
| `adapted` | `false` |
| `reviewed` | `false` |
| `review_status` | `unreviewed` |
| `license` | `MIT` |
| `reconstruction` | `P4.1` |

No historical P4 or human-review claims.

---

## 7. Duplicate / leakage (QC)

| Check | Result |
|-------|--------|
| Exact duplicate episodes | **0** |
| Duplicate IDs | **0** |
| Duplicate attack payloads | **0** |
| v0 `user_query` collision | **0** |
| Lexical near-duplicate (cross-pair, Jaccard ≥0.92) | **0 warnings** (after excluding twins) |
| Attack/benign payload contamination (heuristic) | **0 issues** |
| **Semantic near-duplicate** | **`NOT_VERIFIED`** (explicit) |

---

## 8. Reproducibility

| Check | Result |
|-------|--------|
| Generator run twice (QC / tests) | **byte-identical output = TRUE** |
| `MANIFEST.json` digest_sha256 | `43835dbbbfdb69ce68e3ddc9240641051fd82340757c60f0f30fcd2c37d65ff9` |

---

## 9. Tests

```
20 passed (pytest -q)
```

Includes: v0 byte-stable hashes, v0 validator, P4.1 JSON Schema, full QC, generator determinism, QC failure on corrupted fixture.

---

## 10. Limitations

1. **Not historical P4** — new synthetic scenarios only.
2. **Human semantic review pending** (`review_status=unreviewed`).
3. **Semantic near-duplicate detection** not performed (`SEMANTIC_NEAR_DUPLICATE: NOT_VERIFIED`).
4. **Harness** still v0-shaped (single user message + docs); multi-turn / tool-output / memory fields are **dataset metadata** for future loaders — not executed by current `agent/loop.py`.
5. P2/P3 markdown artifacts were absent; taxonomy enums are defined in `schema/episode.v1.json` for P4.1.
6. No train/eval split assignment yet.

---

## 11. Gate

**`P4.1 PASS WITH CONDITIONS`**

Conditions: semantic near-duplicate verification unavailable; human P5 review not started; extended v1 fields not yet consumed by harness.

P5 was **not** started.
