# AIB P4.2 Dataset Quality Report

## Executive summary

P4.2 candidate dataset: **200 episodes** (100 attack / 100 benign / 100 pairs), schema **episode.v2.json**, deterministic generator with byte-identical regeneration **PASS**. Automated QC **PASS**. Scientific gate: **PASS WITH CONDITIONS** (unreviewed authorship, partial harness execution, n-gram near-duplicate review flags).

## Dataset purpose

Expand coverage beyond frozen P4.1 pilot while preserving defense-agnostic episode definitions suitable for D0/D1/D2 evaluation adapters.

## Size and balance

| Metric | Value |
|--------|------:|
| Episodes | 200 |
| Attack | 100 |
| Benign | 100 |
| Pairs | 100 |

## Taxonomy coverage

All ten V2 families present (see `docs/AIB_P4_2_TAXONOMY_V2.md`). Partitions: development 60 / validation 20 / test 20 attack pairs.

## Duplicates

| Check | Result |
|-------|--------|
| Exact JSON duplicates | 0 |
| Duplicate attack payloads | 0 |
| Intra-P4.2 ACF exact duplicates (attacks) | 0 |

## Semantic deduplication

- Method: ACF + character 5-gram Jaccard (threshold 0.88) via `scripts/semantic_dedup_p4_2.py`
- Cross-corpus: P4.2↔P4.2, P4.2↔P4.1, P4.2↔v0
- **embedding-based semantic paraphrase detection: not performed**
- Near-duplicate flags (review queue): **114** pairs at n-gram ≥0.88 (structural similarity in templated families); no automatic removal

## Leakage

`scripts/qc_p4_2.py` partition leakage checks: **PASS** (no identical queries/payloads/ACF across dev/validation/test; no P4.1/v0 query overlap detected).

## Provenance

All episodes: `provenance_type=programmatically_generated`, `review_status=unreviewed`, `synthetic=true`, seed `42020260920`, timestamp `2026-09-20T00:00:00Z`.

## Human review

**Not performed** in this phase. No `human_reviewed` claims.

## Executability

See `docs/AIB_P4_2_EXECUTABILITY_MATRIX.md`. Only 34/100 attack episodes are fully executable on harness v0 without adapter extensions.

## Reproducibility

| Check | Result |
|-------|--------|
| Generator double-run byte identity | PASS |
| MANIFEST `digest_sha256` | `416264027c5e1f57a2a77f8ca31009f1b6ce399eddc1792a3dc8737ec75e74b3` |

## Scientific acceptance gates

| Gate | Result |
|------|--------|
| A Structural (schema) | PASS |
| B Integrity (exact dupes) | PASS |
| C Pairing | PASS |
| D Taxonomy | PASS |
| E Semantic consistency | PASS (automated) |
| F Leakage | PASS |
| G Reproducibility | PASS |
| H Provenance | PASS |
| I Executability | PASS WITH CONDITIONS (partial execution) |
| J Human review | PASS WITH CONDITIONS (unreviewed) |

## Final gate

**PASS WITH CONDITIONS**

## Limitations

1. Episode count 200 (not 400) to avoid low-mechanism templating.
2. Harness v0 does not inject conversation, tool_results, memory, cross_context, multi-agent, or adaptive traces.
3. Near-duplicate n-gram flags require human adjudication before freeze.
4. No embedding-based deduplication.
5. No live LLM or judge validation of attack success.

## P4.1 / v0 impact

P4.1 mutation: **NONE** (verified). v0 mutation: **NONE** (byte-stable fixtures).
