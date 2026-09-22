# AIB P4.3 — Dataset Plan (updated)

**Status:** **Additive candidate created** for confirmed gap **G5-001** only.  
**Frozen baseline:** P4.2 digest `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee` (immutable).

## External benchmark → gap → response

```text
Tensor Trust / HouYi / StruQ (S1-style deviation)
        ↓
G5-001 confirmed (0 S1 attacks in P4.2)
        ↓
4 paired synthetic episodes (minimum necessary)
        ↓
data/episodes_p4_3/ + schema/episode.p43.v1.json
        ↓
Human adjudication (required before freeze)
```

## Not in scope for this P4.3 increment

- AgentDojo / InjecAgent environment replication (G9/G6)  
- BIPIA / Tensor Trust text import (license + DO_NOT_IMPORT)  
- Harness tool catalog expansion  
- P4.2 byte changes  

## Generators

| Artifact | Role |
|----------|------|
| `scripts/p4_3_gap_episode_bank.py` | Gap-only pair specs |
| `scripts/gen_p4_3_dataset.py` | Deterministic writer + MANIFEST |
| `scripts/qc_p4_3.py` | Schema, S1 checks, P4.2 ACF collision, regen |

## Next steps

1. Human review of `artifacts/p4_3_review_queue.json` (8 items).  
2. Extend P7 scoring notes for **S1** primary metric (evaluation layer; not done here).  
3. Additional gaps (G6/G9) only after harness or protocol decisions — **not** episode inflation.

See `docs/AIB_P4_3_EXTERNAL_BENCHMARK_AUDIT.md` and `docs/AIB_P4_3_GAP_ANALYSIS.md`.
