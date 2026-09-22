# AIB — Final research / publication readiness

## 1. Current status

`RESEARCH / PUBLICATION READY — CURRENT CLAIMS` (descriptive, COV-A n=9; bounded by §4–§6).

## 2. Verified evidence index

| Evidence | Status | Path |
|----------|--------|------|
| P4.2 freeze | verified | `config/p4_2_primary_research_protocol_freeze.v1.json` |
| P4.3 integrity | verified | `config/p4_3_paired_eval_contract.v1.json`, `scripts/verify_p4_3_integrity.py` |
| P4.4 freeze | verified | `scripts/verify_p4_4_freeze.py`, `verify_p4_4_v2_freeze.py` |
| P5 decisions | verified | `docs/AIB_PHASE5_RESEARCH_DECISION_SHEET.md` |
| P6 historical run 173736 | verified | `results/p4_2_paired/p42-primary-d0-d2-20260921T173736Z-controlled/` (167 tracked files) |
| P6 run 130300 | not recovered | **NOT IN REPOSITORY** |
| P7 analysis | verified | `docs/AIB_P7_4_MODEL_LOCK_REPORT.md` (`DESCRIPTIVE_METRICS_RECONCILED`) |
| P8 audit | verified | `docs/AIB_P8_SUBMISSION_READINESS.md` |
| AdaptiGuard pin | verified | `config/adaptiguard_version_pin.v1.json` |
| Model lock | verified | `config/p4_3_live_eval_gate.v1.json`, `docs/AIB_P7_4_MODEL_LOCK_REPORT.md` |
| CI | verified | `.github/workflows/research-ci.yml` |

Reproducibility chain: `docs/AIB_REPRODUCIBILITY_INDEX.md`.

## 3. Primary results (tracked run `…173736Z…`, from `RESULTS.json` + scorer)

| Metric | D0 | D2 |
|--------|----|----|
| ASR | 1/9 (11.11%) | 1/9 (11.11%) |
| Utility (benign) | 9/9 | 9/9 |
| FPR (benign) | 0/9 | 0/9 |

- Records: 36 (18 D0 + 18 D2); judge failures: 0.  
- Observed ΔASR: 0 (descriptive only).

### Paired attack transitions (same episode, D0 → D2)

| Transition | Count |
|------------|------:|
| success → success | 1 |
| success → failure | 0 |
| failure → success | 0 |
| failure → failure | 8 |

## 4. Claim boundary

**Supported:** controlled paired descriptive evaluation; COV-A primary pool (9+9); observed ASR/Utility/FPR; paired transitions; reproducible run manifest and scorer path.

**Not supported by current evidence:** statistical significance; population-level efficacy; generalization; superiority; proven universal defense effectiveness; SOTA; Q1/Q2 journal outcome.

See `docs/AIB_P8_SUBMISSION_READINESS.md` §9.

## 5. Reproducibility

`docs/AIB_REPRODUCIBILITY_INDEX.md`.

## 6. Limitations (canonical references)

1. Primary n=9 attack + 9 benign — `docs/AIB_P8_SUBMISSION_READINESS.md` §3  
2. Descriptive design — protocol freeze `statistics: DESCRIPTIVE_ONLY`  
3. No confirmatory inference — P5 / P8  
4. `upstream_weight_revision = UNVERIFIED` — protocol freeze  
5. Judge operational; no human IAA — P8 §5  
6. Missing `130300` — P8 §2  
7. Track A/B not evidenced in repo — P8 §6  
8. P4.1 harness surface limits — `docs/AIB_P6_LIMITATIONS_ANNEX.md`

## 7. Missing evidence

`p42-primary-d0-d2-20260922T130300Z-controlled` — **NOT RECOVERED / NOT IN REPOSITORY**. Do not cite as in-repo reproducible evidence.

## 8. Manuscript readiness

| Item | Status |
|------|--------|
| Research question | PARTIAL (`docs/AIB_RESEARCH_CONTROLLED_DEFENSE_EXPERIMENT_SPEC.md`) |
| Threat model | PARTIAL (taxonomy + dataset docs) |
| Attack taxonomy | READY (`data/episodes_p4_2`, freeze reports) |
| Defense description | READY (`docs/ADAPTI_GUARD_BRIDGE.md`, D2 gate) |
| Dataset description | READY (P4.2/P4.4 freeze docs) |
| Experimental protocol | READY (freeze + manifest) |
| Evaluation metrics | READY (`config/p4_3_evaluation_metrics.v1.json`, scorer) |
| Primary results | READY (§3 tables; `RESULTS.json`) |
| Secondary results | PARTIAL (paired defense rate n=1 denominator; descriptive) |
| Paired analysis | READY (§3 transitions) |
| Limitations | READY (§6) |
| Reproducibility | READY (`AIB_REPRODUCIBILITY_INDEX.md`) |
| Citation basis | PARTIAL (`docs/AIB_P4_3_EXTERNAL_BENCHMARK_AUDIT.md`; some refs UNVERIFIED) |
| Evidence index | READY (§2) |

**Manuscript source file:** not in repository (P8 §8).

## 9. Tables for manuscript (derived from verified artifacts)

### Table 1 — Experimental design

| Field | Value |
|-------|--------|
| Conditions | D0 (no defense), D2 (AdaptiGuard) |
| Population | COV-A: 9 attack + 9 benign |
| Target model | `openai/gpt-4o-mini-2024-07-18` |
| Judge | `meta-llama/llama-3.3-70b-instruct` |
| Seed | `43020260921` |
| Evaluation | Descriptive paired |

### Table 2 — Primary metrics

| Metric | D0 | D2 | Δ (descriptive) |
|--------|----|----|-----------------|
| ASR | 1/9 | 1/9 | 0 |
| Utility | 9/9 | 9/9 | 0 |
| FPR | 0/9 | 0/9 | 0 |

### Table 3 — Paired transitions (attacks)

See §3.

### Table 4 — Evidence / limitations

| Item | Status | Implication |
|------|--------|-------------|
| n=9 primary | fixed | No population inference |
| 130300 | missing | Cannot claim P6 re-run in git |
| Weight revision | UNVERIFIED | No weight-sensitive defense claims |
| Track A/B | not in repo | Exclude or external supplement |

## 10. Figure readiness (no generation in CI phase)

From existing `RESULTS.json` / scorer output (offline):

1. Bar: D0 vs D2 ASR (1/9 each)  
2. Bar: Utility and FPR (9/9, 0/9)  
3. Paired transition counts (1/0/0/8)

No checked-in figure binaries required; plot from verified counts only.

## 11. Literature / citation audit

Primary mapping: `docs/AIB_P4_3_EXTERNAL_BENCHMARK_AUDIT.md` (AgentDojo, InjecAgent, Tensor Trust, PIArena, etc.).  
**MANUAL VERIFICATION REQUIRED** for Task Shield, Spotlighting, VIGIL as standalone primary artifacts.

## 12. Q1 positioning (non-claim)

Current evidence supports a **controlled descriptive benchmark paper** with explicit n=9 bounds. It does **not** establish population-level efficacy, statistical superiority, generalization, or SOTA. Journal targeting = **MANUAL NEXT STEP**.

## 13. Remaining human actions

- Author manuscript (out of repo).  
- Optional offline archive for `130300` if retained locally.  
- Branch protection / required checks (admin).  
- Optional release tag.  
- Complete citation metadata for UNVERIFIED external defenses.
