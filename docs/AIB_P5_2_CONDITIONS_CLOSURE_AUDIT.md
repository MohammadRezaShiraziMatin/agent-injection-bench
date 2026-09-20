# AIB P5.2 Conditions-Closure Audit

**Type:** Audit gate only (no implementation, no new data, no LLM/API)  
**Date:** 2026-09-20 (UTC)  
**Inherited gate:** P5.1 **PASS WITH CONDITIONS** (`docs/AIB_P5_1_TARGETED_REVISION_REPORT.md`)

---

## 1. Scope

This audit evaluates whether the three P5.1 open conditions are **closed by existing repository evidence**:

1. `semantic_near_duplicate = NOT_VERIFIED`
2. Human review (`review_status=unreviewed`)
3. Harness does not load P4.1 extended context fields (`tool_results`, `cross_context`, `conversation`, `memory_store`)

**Out of scope:** P6/P7, harness implementation, schema changes, episode edits, git commits.

---

## 2. Baseline inherited from P5.1

| Item | Verified value (this audit) |
|------|-----------------------------|
| `HEAD` | `6bced24ea34b9325d3d983ead6ff967d469d1378` |
| Branch | `main` |
| v0 validation | `n=42`, `errors=0`, `ok=true` |
| `git diff -- data/episodes/` | **0 bytes** |
| P4.1 episodes | **20** (10 attack + 10 benign), IDs/pairs unchanged |
| P5.1 modified episodes | **14** (per P5.1 report; unchanged since) |
| `MANIFEST.json` digest | `766814d37385a5650abc0fb4b677ad513939a52312b97fd6babdb9a383dc4007` |

---

## 3. Semantic near-duplicate audit

### 3.1 Existing deterministic mechanisms (verified)

| Layer | Mechanism | Location | What it checks |
|-------|-----------|----------|----------------|
| **Exact duplicate** | Canonical JSON equality | `scripts/qc_p4_1.py` (`json.dumps(ep, sort_keys=True)`) | Full episode object identity |
| **Duplicate IDs / payloads** | Set uniqueness | `scripts/qc_p4_1.py` | Episode IDs; attack `injection.payload` strings |
| **Lexical (query) similarity** | Token Jaccard on `user_query` (threshold ≥ 0.92), excluding same `pair_id` | `scripts/qc_p4_1.py` (`normalize_text`, `jaccard`) | **Word-overlap on user queries only** — not payloads, docs, or attack semantics |
| **v0 query collision** | Exact string match vs v0 + examples | `scripts/qc_p4_1.py` (`load_v0_queries`) | Cross-corpus `user_query` leakage |
| **Template repetition** | Count `(family, technique)` on attacks | `scripts/qc_p4_1.py` | Warns if same pair > 2 (warning only) |
| **Attack/benign contamination** | Substring heuristic on benign docs | `scripts/qc_p4_1.py` | Payload text in benign `retrieved_docs` |

QC explicitly sets:

```text
semantic_near_duplicate: NOT_VERIFIED
```

(`scripts/qc_p4_1.py` line ~209 — hardcoded; not computed from embeddings or semantic models.)

### 3.2 What was run (this audit)

- `python scripts/qc_p4_1.py` → `ok: true`, `warnings: []`, `semantic_near_duplicate: NOT_VERIFIED`
- No other script in the repository implements semantic embedding, paraphrase detection, or attack-template clustering.

### 3.3 Can `semantic_near_duplicate` be VERIFIED from existing evidence?

**No.**

**Verified (deterministic):**

- Exact duplicate episodes: **0** (QC)
- Duplicate attack payloads: **0** (QC)
- P4.1 ↔ v0 exact `user_query` collisions: **0** (QC)
- Cross-pair lexical query Jaccard ≥ 0.92 (excluding twins): **0 warnings** in current QC run

**Not verified (semantic):**

- Same attack mechanism with reworded payloads across episodes
- Structural template reuse (e.g. repeated `send_email` + `search_docs` pattern) beyond `(family, technique)` counts
- Semantic similarity between P4.1 and v0 **attack patterns** (only exact query match is checked)
- Paraphrase or embedding-based near-duplicates

**Missing evidence for semantic verification:**

- No approved offline semantic similarity specification in-repo
- No deterministic semantic fingerprint (e.g. normalized attack-graph hash) beyond lexical Jaccard on queries
- No human-labeled duplicate adjudication log

**Minimum future verification method (proposed only — not implemented):**

1. Document a frozen **attack-signature normalization** (e.g. canonicalize `{source, locus, target_tool, objective}` + normalized payload skeleton).
2. Run pairwise comparison on signatures + normalized payload token sets with explicit thresholds.
3. Optional: human adjudication sample for borderline pairs.

Until such a method is specified and executed, status remains **`semantic_near_duplicate = NOT_VERIFIED`**.

### 3.4 Distinction (explicit)

| Term | Status in repo |
|------|----------------|
| Exact duplicates | **Checked** — QC |
| Lexical near-duplicates (query Jaccard) | **Partially checked** — queries only, threshold 0.92 |
| Semantic near-duplicates | **NOT_VERIFIED** — no valid mechanism |

---

## 4. Human-review audit

### 4.1 Evidence searched

- All 20 files under `data/episodes_v1/{attack,benign}/`
- `schema/episode.v1.json` (`provenance.review_status` const `unreviewed`, `reviewed` const `false`)
- Docs: P5, P5.1, P4.1 plan/report (no human sign-off artifacts)

### 4.2 Findings (verified)

| Field | All 20 episodes |
|-------|-----------------|
| `provenance.review_status` | **`unreviewed`** |
| `provenance.reviewed` | **`false`** |
| `provenance.human_authored` | **`false`** |
| `provenance.synthetic` | **`true`** |
| `provenance.reconstruction` | **`P4.1`** |

**No legitimate human-review evidence found:** no reviewer identity, review date, adjudication log, signed checklist, or `review_status` value other than `unreviewed`. Automated P5/P5.1 agent review is **not** substituted for human review.

**Schema constraint:** `episode.v1.json` fixes `review_status` to `"unreviewed"` (`const`). Closing human review in data would require a **future schema/process change** plus actual human adjudication — outside P5.2 audit scope.

**Open condition:** Human review **not performed**; retain `review_status=unreviewed`.

---

## 5. Harness-context audit

### 5.1 Code verification

**File:** `agent/loop.py`

| P4.1 field | Loaded into harness prompt / loop? | Evidence |
|------------|-----------------------------------|----------|
| `retrieved_docs` | **Yes** | `_docs_block(episode)`; user message includes retrieved documents |
| `user_query` | **Yes** | `user_task = episode["user_query"]` |
| `tool_results` | **No** | No reference in `agent/` |
| `cross_context` | **No** | No reference in `agent/` |
| `conversation` | **No** | Single user message only; no prior turns appended |
| `memory_store` | **No** | No reference in `agent/` |
| `session_state` | **No** | No reference in `agent/` |

Dry-run and live paths share the same message construction (lines 73–81).

### 5.2 Dataset usage of extended fields (static)

| Field | Episodes containing field (of 20) |
|-------|-----------------------------------|
| `tool_results` | 4 |
| `cross_context` | 4 |
| `conversation` | 4 |
| `memory_store` | 2 |
| `session_state` | 2 |

These episodes **cannot be fully exercised** by the v0 harness as shipped; only `retrieved_docs` + final `user_query` affect the default loop.

### 5.3 Intentional vs undocumented?

**Classification: (A) Intentional scope limitation, documented.**

| Source | Statement |
|--------|-----------|
| `docs/AIB_P4_1_DATASET_PLAN.md` §5–6 | v0 harness fields vs P4.1 metadata; semantic near-dup not verified |
| `docs/AIB_P4_1_DATASET_REPORT.md` §10 | Harness does not consume v1-only fields |
| `docs/AIB_P5_1_TARGETED_REVISION_REPORT.md` | Harness limitation explicitly not modified in P5.1 |
| `docs/AIB_P5_DATASET_QA_REPORT.md` | Harness coupling called out |

**Not closed as an implementation gap:** this remains a **documented operational limitation** until a future harness loader (out of scope). P5.2 does **not** treat harness scope as a condition that must disappear for dataset-metadata QA; it remains an **open freeze/runtime condition** for end-to-end runs.

---

## 6. Deterministic regression results

| Check | Command / artifact | Result |
|-------|-------------------|--------|
| v0 validation | `python scripts/validate_episodes.py` | **ok**, n=42, errors=0 |
| P4.1 QC | `python scripts/qc_p4_1.py` | **ok**, issues=[], semantic_near_duplicate=NOT_VERIFIED |
| Byte-identical regen | QC `byte_identical_regeneration` | **true** |
| Tests | `pytest -q` | **20 passed** |
| v0 filesystem | `git diff -- data/episodes/` | **empty** |

No live LLM/API or AdaptiGuard evaluation was run.

---

## 7. Exact remaining conditions

| # | Condition | P5.2 status | Closable without new work? |
|---|-----------|-------------|----------------------------|
| 1 | Semantic near-duplicate verification | **OPEN** — `NOT_VERIFIED` | **No** — needs defined method + execution |
| 2 | Human review | **OPEN** — all `unreviewed` / `reviewed=false` | **No** — needs human process (+ likely schema update) |
| 3 | Harness v1 fields not loaded | **OPEN (documented)** — intentional v0 scope | **No** for runtime E2E; **Yes** as “documented limitation” only |

**Benign taxonomy note (P5.1):** `instruction_deviation` on benign controls remains a schema workaround — not re-audited for closure here; still a metadata limitation.

---

## 8. Promotion decision: P5.1 → PASS?

**Cannot promote.** P5.1 **PASS WITH CONDITIONS** remains appropriate.

| Criterion for unconditional PASS | Met? |
|----------------------------------|------|
| Semantic near-duplicates verified or N/A with approved method | **No** |
| Human review completed with evidence | **No** |
| Harness loads all P4.1 attack channels | **No** (and not required for this audit to document) |

Closing conditions **1** and **2** requires work **outside** this audit. Condition **3** is acknowledged and documented but still limits benchmark execution fidelity for 12+ episode fields.

---

## P5.2 STATUS: CONDITIONS REMAIN

**P5.1 gate remains:** `PASS WITH CONDITIONS` (unchanged).

---

## Files inspected (this audit)

- `docs/AIB_P5_1_TARGETED_REVISION_REPORT.md`
- `docs/AIB_P5_DATASET_QA_REPORT.md`
- `docs/AIB_P4_1_DATASET_PLAN.md`
- `docs/AIB_P4_1_DATASET_REPORT.md`
- `schema/episode.v1.json`
- `schema/episode.schema.json` (v0)
- `scripts/qc_p4_1.py`
- `scripts/gen_p4_1_dataset.py` (referenced; not modified)
- `scripts/validate_episodes.py`
- `agent/loop.py`
- `data/episodes_v1/**/*.json` (20 episodes + `MANIFEST.json`)
- `tests/test_p4_1_dataset.py` (via pytest)

**Repository mutations in P5.2:** **none** (this report only).
