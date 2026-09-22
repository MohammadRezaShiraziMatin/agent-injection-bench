# Research-Grade Controlled Defense Experiment Specification (D0 vs D2)

**Type:** Design/specification only — no live execution by this document.  
**References:** `docs/AIB_COVERAGE_AWARE_EVALUATION_PROTOCOL.md`, `config/p4_3_paired_eval_contract.v1.json`, `experiments/detector_coverage_gap_v1/`, historical run `p43-d0-d2-20260921-controlled` (immutable).  
**P4.2 primary freeze (descriptive):** `docs/AIB_PHASE5_RESEARCH_DECISION_SHEET.md`, `config/p4_2_primary_research_protocol_freeze.v1.json` — COV-A 9+9 paired pool; ASR primary endpoint; not a powered confirmatory study.

---

## 1. Research question (falsifiable)

**RQ-D2-1:** For episodes in stratum **COV-A or COV-B** (per-episode coverage tag), does enabling AdaptiGuard (D2) versus no defense (D0) change **paired** outcomes on the same frozen episode under locked target/judge—specifically attack success (ASR / S1 criterion), S2 forbidden proposal, S3 unauthorized forbidden execution, S4 external side effect, benign utility, and FPR—holding all non-defense variables fixed?

**Falsification:** If paired ASR (and stratum-specific S2/S3/S4 rates) are identical for all episodes in the primary stratum with valid traces, RQ is not supported **for that stratum** (descriptive null; not a proof of universal ineffectiveness).

**Out of scope for RQ:** SOTA, generalization beyond labeled strata, indirect-injection universe, detector calibration (separate experiment).

---

## 2. Hypotheses (measurable)

| ID | Statement | Measurable criterion (paired, same episode) |
|----|-----------|---------------------------------------------|
| **H1** | D2 reduces attack success vs D0 | Δ `attack_success` = D0 true → D2 false on ≥1 episode in primary stratum; stratum ASR(D2) < ASR(D0) with same denominator |
| **H2** | D2 reduces S2/S3/S4 incidence vs D0 | Δ on `forbidden_tool_proposed`, `forbidden_tool_executed` (S3 evidence), `external_side_effect_observed` per existing scorer |
| **H3** | D2 does not materially harm utility or inflate FPR | **Descriptive** comparison: Utility(D0/D2), FPR(D0/D2), Δ on matched benigns; no automated confirmatory τ gate (see Phase 5 freeze) |

**Strata (frozen P4.2 primary):** **COV-A = primary** effectiveness stratum for the 9+9 paired design (`artifacts/p4_2_primary_d0_d2_experiment/MANIFEST.json`). **COV-B = secondary/extension** (not in the frozen primary pool). **COV-C** excluded from primary effectiveness claims (diagnostic appendix). Broader exploratory analysis across COV-A ∪ COV-B may be defined in a **future** protocol extension—not the frozen P4.2 primary descriptive run.

---

## 3. Variables

**IV:** `defense_condition` ∈ {D0, D2}; D0 `defense_enabled=false`, D2 `defense_enabled=true`, AdaptiGuard pinned `30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64`.

**Controlled (identical D0/D2):** frozen dataset digest; episode_id, order, pairing; target/judge model IDs and OpenRouter provider order; `allow_fallbacks=false`; generation block in `config/p4_3_live_eval_gate.v1.json`; system prompt hash; scoring via `map_live_result` / `config/p4_3_evaluation_metrics.v1.json`; attack payload (episode JSON); harness version except defense path.

**DVs (existing definitions only):** ASR, S1 success rate (S1-eligible attacks), S2/S3/S4 rates, Utility, FPR; Paired_Defense_Rate only if same-run D0 baseline and operational definition in paired contract; paired transitions (success→success, success→failure, failure→success, failure→failure); per-episode `defense_event` (detector_result, decision, target_reached) for **detector-observed** reporting layer.

---

## 4. Coverage-aware sampling

| Class | Use in experiment |
|-------|-------------------|
| **COV-A** | Primary effectiveness stratum (detector hit on C1-equivalent input or documented positive); **frozen P4.2 primary pool** |
| **COV-B** | Secondary/extension stratum if calibration incomplete but semantic overlap—tag required; **not** in frozen 9+9 primary pool |
| **COV-C** | **Excluded from H1–H3**; diagnostic/robustness appendix only (P4.3 four attacks = COV-C per gap v1) |
| **COV-U** | Exclude from effectiveness; report as insufficient evidence |

**P4.3 (8 episodes):** Frozen; **not** primary effectiveness population (all attacks COV-C). Prior D0/D2 paired live is **coverage-limited observation**, not defense effectiveness.

**P4.2 (200 episodes):** Candidate **pool** for future primary experiment **after** per-episode coverage labeling (offline calibration protocol like `detector_coverage_gap_v1` or batch `EpisodeInput` probe). **Do not select subset in this spec**—selection criteria only:

- Include attack episodes with `coverage_class` ∈ {COV-A, COV-B} for primary analysis.
- Include all benign episodes paired or matched by design for utility/FPR.
- Exclude or appendix-only COV-C/U unless explicitly labeled diagnostic run.

---

## 5. Experimental design

**Unit:** episode × condition (paired).

```
same episode_id, same input_hash
  → D0 (then) D2  [deterministic order per paired contract]
  → separate raw dirs; never overwrite historical runs
```

**New run:** new `run_id`; manifest records `coverage_class` per episode, digests, model lock evidence, AdaptiGuard SHA.

**Confound control:** comparability audit (`audit_paired_comparability.py`) must PASS before metrics.

**Primary experiment population:** Labeled P4.2 (or future extension) — **not** P4.3 alone for effectiveness claims.

**Frozen P4.2 primary descriptive evaluation:** 9 COV-A attack episodes + 9 pair-matched benigns; **primary endpoint ASR**; repetition_count=1 for the immutable historical controlled run; formal hypothesis testing **deferred**.

---

## 6. Statistical / descriptive plan

**Default:** `descriptive / paired analysis only` (frozen P4.2 primary n=9 attack pairs — **not** a powered confirmatory study).

Report: paired deltas per episode; stratum-aggregated rates with **n, numerator, denominator**; coverage-stratified tables (overall vs COV-A/B vs COV-C appendix).

No winner/ranking/superiority language. Optional exploratory tests only if pre-registered **and** n and assumptions met—otherwise omit.

**Defense Rate:** Report only when paired contract denominator valid; not reinterpreted for COV-C stratum as defense failure.

---

## 7. Failure attribution (evidence-gated)

| Category | When attributable |
|----------|-------------------|
| Detector limitation | COV-C or D1 calibration; `no_hit` + allow with unchanged ASR |
| Bridge/input mapping | Comparability failure or probe D4 |
| Harness/runtime | pre-target-only hook; missing defense trace |
| Target-model behavior | D0/D2 same target_reached and same judge outcome despite D2 block expected |
| Scoring limitation | mapper/judge vs execution evidence disagreement (corrected analysis path) |
| Experiment-size limitation | n too small for stratum claim |
| Dataset coverage limitation | COV-C dominance in run |
| Provider reproducibility | UNVERIFIED weight revision; seed not honored |

No attribution without trace evidence.

---

## 8. Stop conditions (pre-run and post-run)

Abort before live inference if any fail:

- P4.2/P4.3 digest mismatch vs gate
- `verify_model_lock` ≠ LOCKED
- `verify_d2_integration` ≠ PASS
- AdaptiGuard repo HEAD ≠ pinned SHA
- `live_d2_inference_allowed` true without explicit approval artifact (gate policy)
- Missing D0/D2 live approval per contract

Abort interpretation if:

- `audit_paired_comparability` mismatch_count > 0
- Missing target/judge/defense trace for scored metric
- Scorer version ≠ manifest
- Unauthorized change to frozen episodes or historical raw paths

---

## 9. Artifacts (future execution)

Required for a compliant run (existing tooling):

- `results/p4_3_paired/<run_id>/` layout per paired runner
- `RUN_MANIFEST` with `coverage_class` per episode
- Reporting per `AIB_COVERAGE_AWARE_EVALUATION_PROTOCOL.md` layers
- No new scorer/dataset/schema in this spec phase

---

## 10. Relation to current evidence

| Observation | Interpretation allowed |
|-------------|------------------------|
| P4.3 paired live: ASR D0=D2=2/4, D2 hit 0/4 | COV-C: no defensive effect **observed**; not effectiveness failure claim |
| gap v1: 4× D1 | Lexical/evidence gap for P4.3 anchors |
| Next effectiveness study | Requires COV-A/B labeled episodes (likely P4.2 post-labeling) |
