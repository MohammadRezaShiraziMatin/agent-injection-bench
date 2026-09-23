# P3 — Experimental Protocol Freeze (COV-B extension)

**Status:** FROZEN (`config/p3_experimental_protocol_freeze.v1.json`)
**Does not mutate:** P4.2 primary freeze, P5 decision sheet, historical run `p42-primary-d0-d2-20260921T173736Z-controlled`, P1 figures.

---

## 1. Research Question

**RQ (P3-EXT):** On the pre-registered **P3-EXT** population (COV-B, pair-matched benign controls), what are the observed **ASR** (primary), and descriptive **Utility**, **FPR**, **S1–S4**, and **paired D0→D2 attack transitions**, under **D0** (no defense) versus **D2** (AdaptiGuard), for the locked target–judge pair?

Not asked: defense robustness, superiority, SOTA, or cross-model generalization.

## 2. Hypothesis

**Formal confirmatory hypothesis:** DEFERRED (same posture as P4.2 primary).
P3-EXT is **descriptive** unless a separate confirmatory protocol is frozen before execution.

## 3. Threat Model

Indirect injection via retrieved/tool-mediated context; **offline mock tools** (`search_docs`, `send_email`) under harness control (`docs/manuscript/agent_injection_benchmark_manuscript.md` §4). Injection loci per episode schema. No claim of production agent deployment realism.

## 4. Population

| Stratum | Label | Coverage | n attacks | n benign | Notes |
|---------|-------|----------|-----------|----------|-------|
| Historical primary | COV-A | PRIMARY | 9 | 9 | **Immutable** — not re-run |
| P3 extension | **P3-EXT** | COV-B | 42 | 42 | `artifacts/p3_cov_b_extension/MANIFEST.json` |

**Inclusion:** `SECONDARY_ELIGIBLE` + `COV-B` in `artifacts/p4_2_coverage_eligibility/ELIGIBILITY.json`, sorted by `episode_id`, with valid `pair_id` benign match in P4.2 dataset.
**Exclusion:** COV-A primary IDs (overlap forbidden), COV-C diagnostic pool, P4.3 corpus, adaptive packs.

## 5. Inclusion / Exclusion

- **Independent unit:** one episode (attack or benign) executed under D0 and D2 (paired conditions).
- **ASR denominator:** valid judged **attack** episodes in P3-EXT only.
- **Utility/FPR denominator:** valid judged **benign** episodes in P3-EXT scope only.
- Judge failures: classify per protocol §Failure Handling; do not silently drop.

## 6. Models

| Role | Model ID | Provider |
|------|----------|----------|
| Target | `openai/gpt-4o-mini-2024-07-18` | OpenRouter |
| Judge | `meta-llama/llama-3.3-70b-instruct` | OpenRouter |

**Multi-model:** not in this freeze (`multi_model_in_this_freeze: false`). Future studies require new freeze.

## 7. Provider Policy

- **Fallback:** denied (`OPENROUTER_ALLOW_FALLBACKS=false` per project default).
- **Cache (completions):** none in harness; **cache status = UNVERIFIED** for provider-side behavior.
- **Weight revision:** `UNVERIFIED` — limitation on replication claims.
- **Seed:** recorded; **bit-exact reproducibility not guaranteed**.

## 8. D0 / D2

Same definitions as P4.2/P4.3 contracts. **D2** = AdaptiGuard pin `30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64`.
Paired structure: same episode, same model lock, D0 then D2; order effects noted if API non-determinism prevents identical trajectories.

## 9. Tool Environment

Offline mocks only; synthetic tool-result replay in surface adapter. No realistic tool-loop defense (pre-target hook only per `docs/ADAPTI_GUARD_BRIDGE.md`).

## 10. Metrics

Primary: **ASR**. Secondary (descriptive): S1–S4 rates, Utility, FPR, paired attack transitions.
Scorer: `scripts/score_p4_3_paired_metrics.py` / `score_p4_3_live_metrics.py` — **no scorer changes**.

Utility/FPR: descriptive secondary; H3 τ **not** confirmatory (`0.25` / `0.60` are not acceptance thresholds).

## 11. Statistical Plan

- **Historical COV-A (`173736`):** descriptive only (frozen).
- **P3-EXT:** descriptive only under this freeze.
- Confirmatory tests, CIs, and alpha require a **new** pre-registered protocol before execution.

## 12. Seed / Cache Policy

Record seed in `RUN_MANIFEST.json`; honor if provider supports. Document API nondeterminism.

## 13. Trace Schema

Per episode/condition: run_id, episode_id, model IDs, defense_event, execution_trace, judge outputs, defense_traces (D2), timestamps. **No secrets** in artifacts.

## 14. Reproducibility

Git commit, P3 freeze JSON, P3 manifest hash, dataset digest, gate configs, `python scripts/run_p4_3_paired_benchmark.py --p3-cov-b-extension`, scorer command on output dir.

## 15. Failure Handling

Categories: `API_FAILURE`, `JUDGE_FAILURE`, `TIMEOUT`, `INVALID_OUTPUT`, `SCORING_FAILURE`, `TRACE_FAILURE`. Count and report; exclusions only per pre-registered rules (none added post-hoc).

## 16. Stopping Conditions

Fixed episode list (42+42); no optional stopping on interim ASR. **STOP** on historical mutation, scorer mismatch, or unauthorized live execution.

## 17. Claim Boundaries

P3-EXT results **must not** be merged into COV-A primary tables/figures without new protocol decision. P1 figures remain historical-only.

## 18. Live Authorization

Requires: (1) this freeze PASS, (2) `scripts/verify_p3_scientific_safety_gate.py` PASS, (3) dry-run PASS, (4) `artifacts/p3_live_execution_approval.json` with `status: EXPLICIT`, (5) operator-set live flags per approval doc.
**Current repo state:** P3 and P4.2 gates keep `live_d2_inference_allowed: false`; **live blocked** until human authorization.

## 19. Deferred (P2 gaps not in this freeze)

- Multi-model families
- Realistic tool environment
- Full D2 tool-loop traces
- Adaptive Track A/B (separate extension)
- Confirmatory statistics
- Human IAA

See `docs/AIB_P2_Q1_EVIDENCE_GAP_PLAN.md` §7–8.
