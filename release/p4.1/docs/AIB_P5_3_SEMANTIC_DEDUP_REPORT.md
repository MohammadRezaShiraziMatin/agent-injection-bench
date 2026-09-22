# AIB P5.3 Semantic Near-Duplicate Verification Report

**Closes P5.2 condition #1 only** (offline; no LLM/API; no episode edits)  
**Date:** 2026-09-20 (UTC)  
**Dataset:** P4.1 `data/episodes_v1/` (20 episodes) vs frozen v0 (42 episodes)

---

## 1. Baseline (verified)

| Check | Result |
|--------|--------|
| `HEAD` | `6bced24ea34b9325d3d983ead6ff967d469d1378` |
| Branch | `main` |
| v0 validation | **42/42**, **0 errors** |
| `git diff -- data/episodes/` | **0 bytes** |
| P4.1 count | **20** episodes |

---

## 2. Existing QC (reused, not duplicated)

Command: `python scripts/qc_p4_1.py --no-repro`

| Check | Result |
|--------|--------|
| Exact duplicate episodes (canonical JSON) | **0 issues** |
| Duplicate attack payloads | **0 issues** |
| P4.1 ↔ v0 exact `user_query` collision | **0 issues** |
| Lexical query Jaccard ≥ 0.92 (cross-pair, excl. twins) | **0 warnings** |
| QC field `semantic_near_duplicate` (legacy) | Still hardcoded `NOT_VERIFIED` in QC — superseded by this P5.3 ACF run for condition closure |

---

## 3. Method: Attack Content Fingerprint (ACF)

### 3.1 Why this method

Local environment inspection found **no** `sklearn`, `sentence_transformers`, or `torch` (no offline embedding models without network download).  

ACF is a **documented, reproducible, deterministic** extension beyond query-only Jaccard:

| Layer | What it detects |
|-------|-----------------|
| Structural | Same attack family/source/locus/target + normalized payload skeleton |
| Exact content | SHA-256 of normalized **fused** attack-relevant surfaces |
| Near content | Character **5-gram Jaccard** on fused surfaces |
| Payload near | Character **4-gram Jaccard** on normalized injection payload skeletons (attacks only) |

This is **not** full semantic paraphrase detection (synonyms with disjoint n-grams may evade ACF). It **is** a defensible offline screen for **high-overlap and structural** near-duplicates across multiple text surfaces.

### 3.2 Dependencies

- Python 3 stdlib (`hashlib`, `re`, `json`, …)
- `scripts/qc_p4_1.py` — `jaccard`, `normalize_text` (query baseline reference only)
- **No** network, **no** LLM, **no** new pip packages

### 3.3 Input fields (per episode)

Fused bundle built from (when present):

- `user_query`
- `retrieved_docs[].text`
- `tool_results[].output`
- `conversation[].content`
- `memory_store[].value`
- `cross_context[].text`
- `injection.payload`

### 3.4 Normalization

1. Lowercase  
2. Replace emails → `<email>`, numbers → `<num>`  
3. Strip punctuation to spaces; collapse whitespace  
4. Payload skeleton uses same normalization  

### 3.5 Similarity metrics & thresholds

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Normalized fused SHA-256 | equality → **DUPLICATE** | Bit-exact same multi-surface content after normalization |
| Attack signature tuple | equality → **DUPLICATE** | Same mechanism class + same skeleton payload |
| Char 5-gram Jaccard on fused surfaces | **≥ 0.88** → **POSSIBLE_NEAR_DUPLICATE** | Stricter than QC’s word Jaccard on queries alone (0.92); 5-grams catch long shared substrings across docs/tool output |
| Char 4-gram Jaccard on payload skeletons (attacks) | **≥ 0.85** → **POSSIBLE_NEAR_DUPLICATE** | Flags near-identical injection wording |

### 3.6 Comparison scope

| Corpus | Pairs | Twin handling |
|--------|-------|----------------|
| **A. P4.1 vs P4.1** | C(20,2) = 190 | Skip same `pair_id` (attack/benign twins) |
| **B. P4.1 vs v0** | 20 × 42 = 840 | N/A |

### 3.7 Classification rules

- **DUPLICATE** — exact fused hash or identical attack signature  
- **POSSIBLE_NEAR_DUPLICATE** — metric ≥ threshold  
- **NO_OBVIOUS_SEMANTIC_DUPLICATE** — no flag (implicit for unlisted pairs)

---

## 4. Results

**Reproducibility command:**

```bash
python scripts/semantic_dedup_p4_1.py
```

(JSON to stdout; same logic as this audit run.)

### 4.1 P4.1 vs P4.1

| Classification | Count |
|----------------|------:|
| DUPLICATE | **0** |
| POSSIBLE_NEAR_DUPLICATE | **0** |
| Flagged pairs | **none** |

All cross-pair comparisons (excluding twins): **NO_OBVIOUS_SEMANTIC_DUPLICATE** under ACF thresholds.

### 4.2 P4.1 vs v0

| Classification | Count |
|----------------|------:|
| DUPLICATE | **0** |
| POSSIBLE_NEAR_DUPLICATE | **0** |
| Flagged pairs | **none** |

No P4.1 episode fused surface matches a v0 episode at DUPLICATE or POSSIBLE thresholds.

### 4.3 Flagged pairs table

*Empty — no candidates for human adjudication.*

---

## 5. Limitations (explicit)

| Topic | Status |
|-------|--------|
| Paraphrase with low character n-gram overlap | **May not be detected** |
| Embedding / LLM semantic similarity | **Not used** (not installed; no download) |
| Shared high-level template (e.g. many `send_email` attacks) | May be **structurally similar** without exceeding n-gram thresholds — not flagged in this run |
| Human review of borderline cases | **Not required** (no POSSIBLE flags) |

---

## 6. VERIFIED vs NOT_VERIFIED

| Statement | Verdict |
|-----------|---------|
| P5.2 “no reproducible semantic method” | **Superseded** — ACF implemented in `scripts/semantic_dedup_p4_1.py` |
| `semantic_near_duplicate` screening executed offline | **VERIFIED** (ACF run complete) |
| Full semantic paraphrase deduplication | **NOT_VERIFIED** (ACF is structural + high-overlap lexical-substring; not embeddings) |

For **P5.2 condition #1** (dataset freeze QA: obvious near-duplicates across surfaces): **closed** under ACF with documented limits.

---

## 7. Final gate

**`P5.3 SEMANTIC DEDUP VERIFIED`**

No **POSSIBLE_NEAR_DUPLICATE** or **DUPLICATE** pairs; **no human adjudication queue** for dedup.

P5.2 conditions **#2 (human review)** and **#3 (harness scope)** remain open — out of P5.3 scope.

---

## 8. Data policy

No episodes were added, deleted, or rewritten. `data/episodes/` unchanged.
