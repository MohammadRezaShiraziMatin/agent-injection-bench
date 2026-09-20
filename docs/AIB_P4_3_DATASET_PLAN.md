# AIB P4.3 — Dataset Plan (evidence-driven)

**Status:** **HARDENING ONLY** — no `data/episodes_v2/` candidate in this pass  
**Date:** 2026-09-20 (UTC)  
**Prerequisite:** Frozen P4.2 digest `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee`

## Decision

Per `docs/AIB_P4_3_DATASET_AUDIT.md`:

```text
DO NOT CREATE P4.3 (episode corpus)
```

P4.2 is **publication-ready as a frozen benchmark artifact** with documented executability boundaries. Further episode generation is **deferred** until a human-approved gap targets **new mechanisms**, not counts.

## If P4.3 is authorized later

### Allowed goals (pick at least one; justify with audit evidence)

| Goal | Example gap | Not sufficient alone |
|------|-------------|----------------------|
| Attack-surface completion | New live-executable multi-agent bus after harness ships | +10 RAG variants |
| Impact-horizon completion | S3-labeled episodes **only** if harness can observe execution vs proposal distinctly | renaming S2→S3 |
| Realistic interaction completion | New multi-turn patterns with conversation replay tested | paraphrase of existing payloads |
| Benchmark robustness | Fill **specific** under-sampled taxonomy cell with HR review | family balance only |

### Additive rules

1. New root: `data/episodes_p4_3/` or repo-standard versioned dir (never mutate `data/episodes_p4_2/`).  
2. Generator: `scripts/gen_p4_2_dataset.py` fork or parameterized v2 with **new seed** recorded in MANIFEST.  
3. Schema: remain `episode.v2.json` unless scientifically required → then `episode.v3.json` + explicit migration doc.  
4. IDs: `atk_p43_###` / `ben_p43_###` collision-safe.  
5. Pairs: 1:1 attack/benign; no copy-edit of P4.2 files.  
6. QC: `config/p4_3_quality_contract.v1.json` gates before any freeze talk.

### Quality contract (machine-checkable)

Executor mapping lives in `config/p4_3_quality_contract.v1.json`.

Additional policies:

| Policy | Rule |
|--------|------|
| Duplicate | Zero ACF collisions among attacks |
| Near-duplicate | n-gram ≥ 0.88 → human ACCEPT/REVISE/REJECT; no silent drop |
| Leakage | No dev/val/test or P4.1/v0 attack overlap |
| Benign | No injection; matched task intent |
| Provenance | `synthetic=true` unless evidenced real-world with citation |
| Freeze | P4.2 digest unchanged when P4.3 is additive |

### Embedding semantic dedup (recommendation only)

**Feasibility:** Not in repo; would need embedding model pin + threshold study.  
**Recommendation:** Run offline screening **after** ACF/n-gram; human adjudication mandatory; do not add `sentence-transformers` without explicit approval.  
**Status:** Documented in quality contract; **not implemented**.

### Human review package

Reuse `artifacts/p4_2_2_hr_audit_trail.json` schema for P4.3. Until 200/N `ACCEPT` (or resolved REVISE), `review_status != accepted` and **no freeze**.

### Defense / D2 neutrality

Dataset design must not encode AdaptiGuard-specific triggers or labels. D2 is evaluation-time only.

## Near-term hardening (no new episodes)

| Action | Owner | Touches P4.2 bytes? |
|--------|-------|---------------------|
| Sync `provenance.review_status` from HR trail | Future metadata-only revision **or** P4.3 manifest overlay | **Yes if in-place** — forbidden on frozen tag |
| Publish executability matrix v2 from `measure_p4_2_harness_coverage.py` | Docs only | No |
| Document S2-only primary metric + S3/S4 mock limits | Benchmark card | No |
| Adjudicate adaptive n-gram cluster in HR appendix | Human | No |

## Freeze gates (P4.3 candidate)

G1–G12 in quality contract — all must PASS plus explicit scientific coverage sign-off.
