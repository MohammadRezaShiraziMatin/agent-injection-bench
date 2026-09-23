# Level B — Experimental Evidence Strengthening Protocol (DESIGN)

**Document ID:** `aib-level-b-experimental-protocol-design-v1`  
**Status:** `DESIGN` — **not frozen**, **not authorized for execution**  
**Evidence level target:** Level B (stronger experimental evidence; not Level C)  
**Supersedes for planning:** extends `docs/AIB_P8_FUTURE_EXPERIMENT_PROTOCOL_DRAFT.md` skeleton; does **not** modify Level A freezes.

**Upstream contracts (read-only):**

- `paper/RESULTS_EVIDENCE.md` — Level A / B / C boundaries  
- `docs/AIB_P2_Q1_EVIDENCE_GAP_PLAN.md` — gap matrix and MV path  
- `config/p4_2_primary_research_protocol_freeze.v1.json` — historical P4.2 primary (immutable)  
- `config/p3_experimental_protocol_freeze.v1.json` — P3-EXT descriptive extension (immutable evidence)  
- `config/p4_3_evaluation_metrics.v1.json`, `config/p4_3_paired_eval_contract.v1.json` — metric definitions  
- `config/adaptiguard_version_pin.v1.json` — AdaptiGuard pin `30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64`

**Level A evidence preserved (must not be mutated by Level B execution):**

| Layer | Run ID | Role |
|-------|--------|------|
| P4.2 primary | `p42-primary-d0-d2-20260921T173736Z-controlled` | COV-A n=9+9 descriptive baseline |
| P3-EXT | `p3-cov-b-ext-20260923T112900Z-controlled` | COV-B descriptive extension only |

P3-EXT **does not** satisfy Level B. Larger n alone **does not** satisfy Level B.

---

## 1. Purpose

Define a **pre-execution** protocol to strengthen evidence from Level A (controlled descriptive) toward **Level B** (stronger experimental evidence with pre-specified design, reproducibility, and optional confirmatory inference) using **fresh immutable run IDs** and **new frozen manifests**—without relabeling P4.2/P3 historical runs.

This document is **protocol design only**. No dataset generation, freeze, live execution, or statistical results are produced here.

---

## 2. Evidence-level boundary

| Level | Meaning in AIB |
|-------|----------------|
| **A (current)** | Immutable P4.2 + P3-EXT descriptive paired evidence; no confirmatory superiority claims |
| **B (this protocol)** | New frozen study: expanded pre-registered population, multi-model matrix (as approved), richer harness/traces, pre-specified SAP, fresh runs |
| **C (out of scope)** | Broad replication, human IAA at scale, adaptive campaigns as primary—separate protocols |

**Forbidden without Level B evidence:** SOTA, superiority, generalization, production-readiness, comprehensive benchmark, robust-defense, Q1-ready claims.

---

## 3. Research question (candidate)

**RQ-B1:** On a **pre-registered** episode pool and **locked** model matrix, does D2 (AdaptiGuard integration per pin) change the **primary endpoint (ASR)** relative to D0 under the paired execution contract, with pre-specified estimands and inferential rules?

Confirmatory wording is **inactive** until `PROTOCOL FREEZE` + `SAP LOCK` (§22).

---

## 4. Estimand (to freeze at SAP LOCK)

**Primary estimand (candidate):** Population proportion of **valid judged attack episodes** with `attack_success = true` under D0 vs D2, on the Level B primary manifest, for each **pre-registered target model** in the model matrix.

**Paired structure:** Same `episode_id` executed under D0 then D2 (order and pairing rules frozen in manifest).

**RESEARCHER DECISION REQUIRED:** Whether Level B primary analysis is **per-model** only, or includes a pre-specified multi-model estimand (e.g., stratified by model family). Document choice at freeze; no post-hoc pooling.

---

## 5. Primary endpoint

**Endpoint:** `ASR` — consistent with P4.2 freeze (`config/p4_2_primary_research_protocol_freeze.v1.json` primary_endpoint).

**Definition:** Per `config/p4_3_evaluation_metrics.v1.json` and paired scorer `scripts/score_p4_3_paired_metrics.py`: attack successes / **valid judged attack episodes** (denominator excludes `JUDGE_FAILURE` per contract).

**Historical P4.2 primary endpoint record remains unchanged.** Level B uses a **new** manifest and run IDs.

---

## 6. Secondary endpoints

Pre-register at SAP LOCK (descriptive + inferential policy per endpoint):

| Endpoint | Source contract | Notes |
|----------|-----------------|-------|
| S2, S3, S4 | P4.2 severity strata | Stratified descriptive tables; confirmatory hierarchy frozen |
| Utility | Paired benign contract | `utility_success` / judge path per `result_mapper` |
| FPR | `p4_3_paired_eval_contract.v1.json#fpr` | Benign denominator rules unchanged |
| Paired transitions | D0/D2 `attack_success` pairs | SS/SF/FS/FF; judge-failure handling per §21 |
| Judge failure rate | Operational QC | Not a success proxy |

No new endpoints added for presentation purposes.

---

## 7. Diagnostic / exploratory analyses

**Diagnostic (labeled, not primary):** per COV stratum, attack family, tool surface, provider route, cache hit rate, retry counts, defense `decision` distribution, partial trace coverage.

**Exploratory (separate protocol):** adaptive attack campaigns (Track A/B), COV-C strata, cross-judge ablations—**not** mixed into Level B primary endpoint.

---

## 8. Population

**Coverage class:** Pre-register one primary class (e.g., expanded COV-A and/or declared COV-B subset)—**RESEARCHER DECISION REQUIRED** at manifest freeze.

**Requirements:**

- Episode IDs listed in a **new** manifest under `artifacts/` with content hash recorded at freeze.  
- Attack count **>** 9 (P4.2 primary attacks)—exact N **not fixed in this design doc**.  
- Benign count pre-specified (paired or matched policy frozen).  
- No post-hoc addition/removal of episodes after any live execution begins.

**Excludes from Level B primary pool:** episodes used only for P4.2 `173736` or P3 `p3-cov-b-ext-…` unless explicitly re-listed in a new manifest (still requires new runs, not mutation of old bundles).

---

## 9. Sample-size rationale

**Gate:** `SAMPLE_SIZE_LOCKED` requires documented **power analysis** (or Bayesian equivalent pre-specified) **before** `PROTOCOL FREEZE` for confirmatory mode.

**Design doc position:**

- Level B **descriptive expansion** may proceed with fixed N justified by coverage goals **only if** confirmatory claims remain disabled.  
- Any **confirmatory** hypothesis requires pre-registered N and effect size assumptions—**RESEARCHER DECISION REQUIRED**; do not invent N here.

**Dependency:** Statistician / researcher supplies power memo → referenced from frozen `config/level_b_protocol_freeze.v1.json` (future artifact, not created in DESIGN phase).

---

## 10. Dataset construction

1. Select episode IDs from `data/episodes_p4_2/` (or successor digest) per coverage rules.  
2. Build manifest: attack IDs, benign IDs, pairing, severity tags, tool expectations.  
3. Compute dataset digest SHA-256; store in freeze JSON.  
4. **No live execution** until `DATASET FREEZE` gate (§22).

P4.2 dataset digest `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee` remains valid for historical layer only.

---

## 11. Attack taxonomy (operational)

Use P4.2 schema labels (S1–S4, interaction types, horizons) already in episode JSON.

**In-scope for Level B primary (candidate families):** indirect prompt injection via retrieved/tool-mediated context aligned with existing harness (mock `search_docs`, `send_email`) and P4.2 episode semantics.

**Out of primary endpoint (extension tracks):**

- Adaptive / multi-turn rewrite campaigns  
- Instruction-hierarchy attacks without frozen episode definitions  
- RAG-only attacks without tool loop evidence  

Each extension requires its own manifest and run ID namespace.

---

## 12. Benign / control population

Benign episodes: task success measured by Utility endpoint; FPR per paired contract.

**Rules frozen before execution:** inclusion of benign episodes with tool-use vs QA-only; expected `utility_answer_contains` / judge labels; no post-hoc relabeling.

---

## 13. Model matrix (DESIGN ONLY until lock)

**Pattern:** Reuse `scripts/verify_model_lock.py` and gate files; one RUN_MANIFEST per target model (or per matrix cell).

| Role | Policy |
|------|--------|
| Target model(s) | **RESEARCHER DECISION REQUIRED:** minimum 2 families for Level B multi-model claim; IDs locked in freeze JSON |
| Judge model(s) | Default: single operational judge locked across matrix unless pre-registered judge ablation (secondary) |
| Provider | OpenRouter (or successor) — **no API calls in DESIGN** |
| Temperature | Record per run (P4.2 primary used provider defaults; Level B must freeze explicit values) |
| Seed | Record; `seed_policy` same as P4.2 freeze wording |
| max_tokens | Freeze per model row |
| Cache | Document policy: completion cache on/off; manifest field required |
| Fallbacks | `OPENROUTER_ALLOW_FALLBACKS=false` unless amended with justification |

No model IDs are authorized here without researcher sign-off and gate artifacts.

---

## 14. Judge policy

- Operational LLM judge for attack success and utility (as Level A).  
- `judge_status == JUDGE_FAILURE` → excluded from valid judged denominators (per P3 precedent `atk_p42_045`).  
- Retries: freeze max judge retries (P3 contract used operational limits).  
- **Optional human IAA** (§24): separate sample; not a substitute for pre-registered primary judge without SAP amendment.

---

## 15. Agent / tool harness

**Minimum loop (must be traceable):**

```text
agent task → untrusted input in context → retrieval/tool → reasoning → tool call → observation → final output
```

**Current gap (GAP — DESIGN ONLY):** P4.2/P3 use offline mocks and pre-target D2 hook (`docs/ADAPTI_GUARD_BRIDGE.md`). Level B requires **documented hook coverage** per tool step for D2.

**Requirement:** Per-episode trace bundle includes: user/trusted instruction, untrusted payload source, model messages, tool requests/responses, defense events, judge I/O hashes (no secrets).

**No parallel harness implementation in DESIGN phase.**

---

## 16. Trace schema

Align with existing `RESULTS.json` / per-episode JSON and `AUDIT_TRAIL.jsonl` patterns.

**Minimum fields per episode (D0 and D2):** `episode_id`, `split`, `defense_enabled`, `attack_success`, `utility_success`, `judge_status`, `defense_event`, execution trace references.

**Level B addition (to specify at freeze):** `trace_schema_version`, `hook_coverage_map`, `tool_step_index` for each defense decision.

---

## 17. Defense configuration

| Condition | Definition |
|-----------|------------|
| **D0** | No defense (passthrough) |
| **D2** | AdaptiGuard `CoreDefensePipeline` via AIB bridge; pin `30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64` unless **new pin** approved in separate amendment |

Level B compares **observed D0/D2 behavior** under integration—**not** efficacy in general.

P3 live gate history remains evidence only; new live requires new approval artifacts (same pattern as P3 `artifacts/p3_live_execution_approval.json`).

---

## 18. Randomization / seed

- Episode order: freeze execution schedule (may be deterministic list).  
- Seed recorded in `RUN_MANIFEST.json`.  
- No re-seeding mid-run to improve metrics.

---

## 19. Provider / cache policy

Manifest must record: provider order env vars, model IDs, weight revision fields (currently **UNVERIFIED** on P4.2—Level B should require `upstream_weight_revision` capture or local replay).

**Cache:** explicit on/off; if on, document invalidation rules for confirmatory analysis.

---

## 20. Failure handling

| Failure type | Policy (freeze detail) |
|--------------|------------------------|
| Transient API | Bounded retries; record in AUDIT |
| Non-judgeable | Exclude from primary denominators if pre-specified |
| Provider outage | Abort run cell; do not substitute models post-hoc |
| Scorer error | Fix forward in code; re-score from raw only with new audit entry |

---

## 21. Exclusion / inclusion rules

**Include in primary ASR:** attack episodes with `judge_status` valid per contract.

**Exclude:** `JUDGE_FAILURE` from attack denominators; document per-episode in reconciliation table.

**Invalid:** schema violations, wrong episode ID, gate bypass—verifier must fail CI.

**No post-hoc exclusion** based on ASR outcomes.

---

## 22. Statistical analysis plan (SAP) — design placeholders

**Inactive until SAP LOCK.** No p-values produced in DESIGN phase.

| Element | Design requirement |
|---------|-------------------|
| Estimand | §4 frozen |
| Primary hypothesis | **RESEARCHER DECISION REQUIRED** at SAP LOCK |
| Null / alternative | Binary ASR difference D0 vs D2 on paired attacks (per model cell) |
| Alpha | Pre-register (e.g., 0.05 two-sided per primary) |
| CI | Method stated (e.g., Wilson/clopper-pearson for proportions; paired methods if justified) |
| Effect size | Pre-specified MDE or equivalence margin if applicable |
| Paired structure | If McNemar (or exact paired test) used, justify discordant-pair estimand |
| Multiplicity | Pre-register hierarchy (primary vs secondary); no fishing |
| Missing data | Judge failures = missing for ASR; no imputation without pre-specified rule |

---

## 23. Multiple-comparison policy

Primary endpoint tested per pre-registered hierarchy. Secondary endpoints: descriptive or gated inferential adjustments—**frozen in SAP**.

Multi-model: if confirmatory, use pre-specified multiplicity control across models—**RESEARCHER DECISION REQUIRED**.

---

## 24. Human evaluation requirements (optional)

If claims depend on subjective success:

- Sample size pre-specified  
- Blinded adjudication guide  
- IAA metric (e.g., Cohen's κ) and threshold  
- Adjudication for disagreements  

**Not executed in DESIGN phase.**

---

## 25. Reproducibility requirements

Freeze before execution:

`dataset version`, `attack/benign IDs`, `model/judge versions`, `provider`, `temperature`, `seed`, `prompt templates`, `defense config`, `AdaptiGuard commit`, `runner git commit`, `dependency lock`, `evaluation window`, `cache/retry policy`.

Each execution → **new** `run_id` under `results/level_b_paired/` (path **RESEARCHER DECISION REQUIRED** at freeze).

---

## 26. Immutable run contract

```text
run_id = <prefix>-<UTC timestamp>-controlled
```

Bundle: `RUN_MANIFEST.json`, `D0/`, `D2/`, `RESULTS.json`, `AUDIT_TRAIL.jsonl`, scorer output artifact, manifest hash.

**Never mutate** `p42-primary-d0-d2-20260921T173736Z-controlled` or `p3-cov-b-ext-20260923T112900Z-controlled` bundles.

---

## 27. Claim boundaries

Level B evidence may support **pre-registered** inferential statements on the **frozen population and model matrix only**.

Still forbidden unless separately evidenced: SOTA, superiority, broad generalization, production readiness, comprehensive coverage, adaptive robustness as primary claim.

---

## 28. Execution gate (hard)

```text
PROTOCOL DESIGN COMPLETE   ← this document (DESIGN)
        ↓
RESEARCHER REVIEW
        ↓
PROTOCOL FREEZE            ← config/level_b_protocol_freeze.v1.json + STATUS=FROZEN
        ↓
SAP LOCK                   ← docs/AIB_LEVEL_B_SAP.v1.md (future)
        ↓
SAMPLE_SIZE_LOCKED         ← power memo referenced
        ↓
DATASET FREEZE             ← manifest hash
        ↓
EXECUTION AUTHORIZATION    ← approval JSON + gate flags
        ↓
FRESH IMMUTABLE RUN
        ↓
ANALYSIS per SAP
```

**This task stops at PROTOCOL DESIGN.**

---

## 29. Acceptance criteria (for future FREEZE sign-off)

- [ ] Manifest hash and episode list approved  
- [ ] Model matrix locked and verifiers pass offline  
- [ ] SAP pre-registered; alpha and multiplicity documented  
- [ ] Sample size justified (power memo) if confirmatory  
- [ ] Trace/harness gap closed or explicitly scoped  
- [ ] Approval artifacts and gates mirror P4.2/P3 patterns  
- [ ] No mutation of Level A historical SHA evidence  
- [ ] CI + integrity verifiers green on freeze commit  

---

## References

- Gap plan MV path: `docs/AIB_P2_Q1_EVIDENCE_GAP_PLAN.md` §8  
- P8 skeleton: `docs/AIB_P8_FUTURE_EXPERIMENT_PROTOCOL_DRAFT.md`  
- Confirmatory V2 / unrelated workflows: **out of scope** for this Level B AIB protocol
