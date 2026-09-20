# AIB P4.2.1 Near-Duplicate Adjudication Report

## 1. Executive result

114 n-gram similarity flags from `scripts/semantic_dedup_p4_2.py` were individually adjudicated using deterministic content, taxonomy, mechanism, and context evidence. **No episode removals or replacements** were required. The P4.2 candidate remains **200 episodes** with manifest digest unchanged.

## 2. Gate result

**PASS WITH CONDITIONS** — automated adjudication complete; human scientific review still pending; embedding-based dedup not performed; n-gram flags remain numerically unchanged (expected).

## 3. Baseline P4.2 state

| Field | Value |
|-------|-------|
| Episodes | 200 (100 attack / 100 benign / 100 pairs) |
| Schema | `schema/episode.v2.json` |
| Seed | `42020260920` |
| Manifest digest | `416264027c5e1f57a2a77f8ca31009f1b6ce399eddc1792a3dc8737ec75e74b3` |

## 4. P4.1 immutability verification

| Check | Result |
|-------|--------|
| Tag `aib-p4.1-frozen-v1.0` | Present |
| `verify_p6_freeze.py` | `ok=true` |
| Digest | `717458789217d4fd29c655e40018471fdaf16b061ff5481cfdc48f7812437ac3` |
| `git diff -- data/episodes_v1/` | Empty |
| Schema `episode.v1.json` | Unchanged |

## 5. v0 immutability verification

| Check | Result |
|-------|--------|
| Episode count | 42 |
| `validate_episodes.py` | `ok=true` |
| `git diff -- data/episodes/` | Empty (0 bytes) |
| Fixture hashes | Unchanged (`tests/test_p4_1_dataset.py`) |

## 6. Git / remote audit

| Item | Finding |
|------|---------|
| Current branch | `cursor/p4-2-dataset-6db2` |
| HEAD | `7e0da39` (matches `origin/cursor/p4-2-dataset-6db2`) |
| `main` | Not modified locally |
| P4.1 tag | Not modified |
| Prior unexpected push | Branch + draft PR **#2** on GitHub (documented; not deleted/force-pushed) |
| P4.2 files on remote | Same commits as local pre-P4.2.1 (schema, generator, `data/episodes_p4_2/`, docs, tests) |
| P4.2.1 changes | **Local only** (this report + adjudication tooling/artifacts) |

## 7. 114-flag methodology

Source: `scripts/semantic_dedup_p4_2.py` with threshold **0.88** (character 5-gram Jaccard on **normalized fused surfaces** from `extract_surfaces` + `normalize_surface`).

Inventory reconstruction: `scripts/adjudicate_p4_2_1.py` calls the same `screen_pairs()` implementation without regenerating episodes.

| Corpus | Flag count |
|--------|------------|
| P4.2↔P4.2 | **114** |
| P4.2↔P4.1 | 0 |
| P4.2↔v0 | 0 |

All 114 flags have `ngram_jaccard=1.0`. They involve **18 attack episodes** (`atk_p42_083`–`atk_p42_100`) in three within-family clusters:

| Cluster | Episodes | Ordered pairs flagged |
|---------|----------|------------------------|
| `cross_context_injection` | 083–092 (10) | 90 |
| `multi_agent_injection` | 093–096 (4) | 12 |
| `adaptive_injection` | 097–100 (4) | 12 |
| **Total** | 18 | **114** |

The detector counts **ordered** pairs (A→B and B→A), hence 114 not 57 unordered.

**Interpretation:** Normalization (`<email>`, `<num>`, punctuation stripping) collapses distinct campus IDs (`CC-P42-01` vs `CC-P42-02`, etc.) onto a shared template while **ACF fingerprints remain unique** (no ACF exact duplicates).

## 8. Adjudication categories

| Category | Count | Action |
|----------|------:|--------|
| FALSE_POSITIVE | 0 | — |
| VALID_VARIANT | **114** | KEEP_BOTH |
| POSSIBLE_DUPLICATE_REQUIRES_HUMAN | 0 | — |
| TRUE_DUPLICATE | 0 | — |

## 9. Complete statistics

- Flags adjudicated: **114 / 114**
- Replacements performed: **0**
- Episodes removed: **0**
- Dataset size after: **200**

## 10. Flag-level evidence

Machine-readable records (all 114): `artifacts/p4_2_1_near_duplicate_adjudication.json`  
Summary CSV: `artifacts/p4_2_1_near_duplicate_summary.csv`

Each record includes: episode IDs, families, pair IDs, n-gram metric/value/threshold, ACF status, payload skeleton comparison, taxonomy comparison, distinguishing variables, fused-surface equality after normalization, adjudication, action, rationale.

**Representative rationale (cluster 083–092):** episodes share normalized fused-surface templates but differ in `user_query`, `injection.payload`, `cross_context` (`context_id`, `label`, `text`), and rotating `taxonomy.technique` / `taxonomy.context_type` — valid controlled variants of cross-context injection channels.

## 11. Replacements

None. No `TRUE_DUPLICATE` classifications.

## 12. Final dataset statistics

Unchanged from baseline (200 / 100 / 100 / 100 pairs).

## 13. Family distribution

Unchanged (10/8/16/10/14/12/12/10/4/4 per family).

## 14. Duplicate status before / after

| Metric | Before | After |
|--------|--------|-------|
| Exact JSON duplicates | 0 | 0 |
| ACF exact duplicates (P4.2 attacks) | 0 | 0 |
| N-gram flags (same detector) | 114 | **114** |

## 15. Leakage status

`scripts/qc_p4_2.py`: **PASS** (unchanged).

## 16. Pairing status

100 attack / 100 benign / 100 pairs — **PASS**.

## 17. Reproducibility status

`scripts/qc_p4_2.py` byte-identical regeneration: **PASS**. Manifest digest unchanged.

## 18. Executability status

Unchanged (34 EXECUTABLE / 58 PARTIAL / 8 DESIGNED_NOT_EXECUTABLE).

## 19. Human-review status

**NOT PERFORMED.** All episodes remain `review_status=unreviewed`.

## 20. Limitations

- N-gram detector uses aggressive normalization; high scores do not imply semantic duplication.
- **Embedding-based semantic paraphrase detection was not performed.**
- Residual 114 flags are **documented and adjudicated**, not eliminated by metric tuning.
- Human scientific review (P4.2.2) still required.

## 21. Files changed (P4.2.1)

- `scripts/adjudicate_p4_2_1.py`
- `scripts/p4_2_1_summary_csv.py`
- `artifacts/p4_2_1_near_duplicate_adjudication.json`
- `artifacts/p4_2_1_near_duplicate_summary.csv`
- `docs/AIB_P4_2_1_NEAR_DUPLICATE_ADJUDICATION_REPORT.md`

## 22. Files not changed

- `data/episodes_p4_2/**` (episode bytes)
- `data/episodes_v1/**`, `data/episodes/**`
- `schema/episode.v1.json`, frozen tag
- `scripts/p4_2_episode_bank.py`, `scripts/gen_p4_2_dataset.py` (generator semantics)

## 23. Next gate

**P4.2.2 — Human scientific review**
