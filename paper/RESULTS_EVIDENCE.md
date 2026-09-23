# Results evidence index (claim-bounded)

This file records **what the repository evidence supports** for claims and venue positioning. It does not replace frozen protocols, raw run bundles, or the canonical paired scorer.

## Evidence / Claim Level

### Current level

**Level A — current descriptive evidence**

AIB’s current evidence is at **Level A**: a controlled, paired, **descriptive** evaluation with immutable run artifacts, explicit frozen protocols, and a reproducible artifact chain. The tracked evidence package includes:

| Layer | Run ID | Population | Role |
|-------|--------|------------|------|
| **P4.2 primary (COV-A)** | `p42-primary-d0-d2-20260921T173736Z-controlled` | 9 attack + 9 benign | Primary descriptive paired baseline |
| **P3-EXT (COV-B)** | `p3-cov-b-ext-20260923T112900Z-controlled` | 42 attack + 42 benign (84 episodes per D0/D2 file) | Separate descriptive extension; not pooled into COV-A primary claims |

P3-EXT remains **descriptive** and does **not** automatically advance the project to Level B. Larger n alone is not a Level B criterion.

### Evidence supporting Level A

- Immutable live run directories under `results/p4_2_paired/` and `results/p3_paired/` (no substitution of missing runs).
- Frozen protocols: `config/p4_2_primary_research_protocol_freeze.v1.json`, `config/p3_experimental_protocol_freeze.v1.json`.
- Paired D0/D2 execution and metrics via `scripts/score_p4_3_paired_metrics.py` (descriptive ASR, Utility, FPR, paired attack transitions).
- Manuscript and figure data derived from scorer output (`docs/manuscript/`, `docs/AIB_P3_VALIDATION_REPORT.md`).
- P3 judge-quality record: D0 judge failures = 1 (`atk_p42_045`); D2 judge failures = 0 (preserved in raw evidence).

**P3-EXT sample metrics (from validation report / `docs/manuscript/figures/p3_figure_data.json`; COV-B only):** D0 ASR 11/41, D2 ASR 11/42, Utility 35/42, FPR 0/42; paired transitions SS=11, FF=31 (SF=0, FS=0). D0 ASR denominator 41 reflects one D0 judge failure among 42 executed attacks.

### Allowed claims (Level A)

- Observed **sample-level** ASR, Utility, FPR, and paired transitions on specified runs, populations, target model, judge, and protocol.
- Protocol compliance, gate/approval provenance, and artifact checksum discipline for cited run IDs.
- **D2 defense integration** and **observed D0/D2 behavior** on the evaluated execution path (AdaptiGuard bridge per pin)—not defense effectiveness in general.
- Descriptive comparison of D0 versus D2 within the same paired episode set.

### Explicit exclusions (not supported at Level A)

- Robust or general defense **effectiveness**, superiority, state-of-the-art, or production readiness.
- Statistical significance, confirmatory inference, or population-level generalization.
- Comprehensive security coverage, adaptive robustness, or multi-model/agent leaderboard claims.
- Any implication that P3-EXT alone satisfies Level B or “Q1-ready” thresholds.

### Level B — stronger experimental submission (future)

Level B requires a **new experimental protocol** and **fresh immutable run IDs**, not relabeling of current runs. Minimum strengthening dimensions (see gap plan) include, where pre-specified: larger registered sample, multiple target models, broader attack coverage, more realistic agent/tool harness, richer D2 traces, independent replication where appropriate, and stronger reproducibility controls. P3-EXT COV-B expansion **does not** by itself constitute Level B.

### Level C — higher security-venue preparation (future)

Level C denotes **higher evidence maturity** for security-oriented venues—not guaranteed acceptance. Illustrative requirements: broader coverage, replication, human annotation / IAA, verified weight revision, evaluation diversity, realistic agent environments, and confirmatory or adaptive designs **only where a new frozen protocol explicitly supports them**.

### Venue positioning (descriptive only)

| Level | Positioning (no ranking) |
|-------|---------------------------|
| A | Workshop / findings / artifact-oriented submission paths aligned with descriptive evidence |
| B | Stronger empirical submission paths after Level B evidence exists |
| C | Higher-evidence security-venue preparation when Level C criteria are met |

### Gap plan reference

Remaining documented gaps and the minimum strengthening path: [`docs/AIB_P2_Q1_EVIDENCE_GAP_PLAN.md`](../docs/AIB_P2_Q1_EVIDENCE_GAP_PLAN.md).

### Canonical Level A statement

> AIB's current evidence is at Level A: a controlled descriptive paired evaluation with immutable run artifacts, including the P4.2 primary evaluation (COV-A, n=9+9) and the subsequent P3-COV-B descriptive extension (42+42 per condition, separate evidence layer). The evidence supports sample-level observations, protocol/artifact provenance, and descriptive D0/D2 behavior—including D2 defense integration on the recorded execution path—but does not establish confirmatory effectiveness, superiority, generalization, or broad robustness. Reaching Level B requires a new experimental protocol and fresh immutable runs covering the documented evidence gaps. The remaining gaps are recorded in `docs/AIB_P2_Q1_EVIDENCE_GAP_PLAN.md`.
