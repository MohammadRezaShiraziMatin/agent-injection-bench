# P2 — Scientific Strengthening / Q1 Evidence Gap Plan

**Status:** Planning & audit only (no experiments executed in P2).
**Audit date:** 2026-09-22 (UTC)
**Repository branch context:** `cursor/p1-evidence-figures-6db2` @ `64ef80b` (includes P1 figures); `main` @ `cdab059` (manuscript; P1 merged via PR pending at audit time).
**Authoritative primary run:** `p42-primary-d0-d2-20260921T173736Z-controlled` (`config/p4_2_primary_research_protocol_freeze.v1.json` → `historical_run_immutable`).

**P2 answers:** What evidence exists, what is missing, why gaps matter, and what must be produced later—without generating new results.

---

## 1. Current Evidence Baseline

### 1.1 Population & design (verified)

| Item | Evidence | Status |
|------|----------|--------|
| Coverage class | COV-A primary | **VERIFIED** (freeze + `RUN_MANIFEST.json` `coverage_by_episode`) |
| Attack episodes (primary ASR denominator) | **n = 9** | **VERIFIED** |
| Benign episodes (Utility/FPR denominator) | **n = 9** (pair-matched to primary attacks) | **VERIFIED** |
| Paired episodes (same `pair_id`, D0 then D2) | **n = 18** unique episodes | **VERIFIED** |
| Judged records (D0 + D2 RESULTS) | **36** rows (`18` per condition) | **VERIFIED** |
| Study type | Controlled paired **descriptive** | **VERIFIED** (freeze `statistics: DESCRIPTIVE_ONLY`) |
| Primary endpoint | ASR | **VERIFIED** (freeze) |
| Conditions | D0, D2 only | **VERIFIED** (no D1 in primary freeze) |
| Repetition | 1 | **VERIFIED** (`repetition_count: 1`) |
| Adaptive in primary | Excluded | **VERIFIED** (`adaptive_scope: EXCLUDED_FROM_P4_2_PRIMARY_PROTOCOL`) |

**Sample-size vocabulary (do not conflate):**

- **Attack n = 9** → ASR and paired attack transition denominators.
- **Benign n = 9** → Utility and FPR denominators (not the full P4.2 benign corpus n=100).
- **18 episodes** → paired design unit (one D0 + one D2 execution per episode).
- **36 records** → condition-split judged rows in `D0/RESULTS.json` + `D2/RESULTS.json` (and combined root `RESULTS.json`).

### 1.2 Models & providers (verified on primary run)

| Item | Value | Status |
|------|-------|--------|
| Target model | `openai/gpt-4o-mini-2024-07-18` | **VERIFIED** (`RUN_MANIFEST.json`) |
| Judge model | `meta-llama/llama-3.3-70b-instruct` | **VERIFIED** |
| Target/judge providers | OpenRouter | **VERIFIED** (manifest) |
| Target families evaluated (live primary) | **1** (single mini GPT-4o snapshot) | **VERIFIED** — limitation |
| Cross-model ASR/utility evidence | None in primary | **NOT VERIFIED** |
| `upstream_weight_revision` | `UNVERIFIED` | **MISSING** (freeze + manifest) |
| Seed | `43020260921` | **VERIFIED** (recorded) |
| Seed / bit-exact replay | Provider may not honor | **PARTIAL** (`seed_policy: record_and_honor_if_provider_supports`) |

### 1.3 Descriptive metrics (independently verified via scorer)

Source: `python scripts/score_p4_3_paired_metrics.py results/p4_2_paired/p42-primary-d0-d2-20260921T173736Z-controlled`
Cross-check: `docs/manuscript/figures/p1_figure_data.json` (P1, when present).

| Metric | D0 | D2 | Judge failures |
|--------|----|----|----------------|
| ASR | 1/9 (11.11%) | 1/9 (11.11%) | 0 |
| Utility | 9/9 | 9/9 | 0 |
| FPR | 0/9 | 0/9 | 0 |

**Paired attack transitions (D0 `attack_success` → D2 `attack_success`):**

| Transition | Count |
|------------|------:|
| success → success | 1 |
| success → failure | 0 |
| failure → success | 0 |
| failure → failure | 8 |

### 1.4 Defense & artifacts

| Item | Evidence | Status |
|------|----------|--------|
| AdaptiGuard commit pin | `30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64` | **VERIFIED** (manifest + `config/adaptiguard_version_pin.v1.json`) |
| D2 `defense_enabled` on attacks | Present in `D2/RESULTS.json` (`defense_event`) | **VERIFIED** (sample: transform/block decisions) |
| D2 defense trace JSON files | 18 under `D2/defense_traces/` | **VERIFIED** (count) |
| D0/D2 target & judge traces | `D0/target_traces`, `D2/target_traces`, `judge_outputs` | **VERIFIED** (directories populated) |
| Paired-defense rate (contract) | Not computable as efficacy claim at n=1 D0-success | **NOT COMPUTABLE** for superiority (1 D0 attack success) |
| Run `…130300Z-controlled` | Not in repository | **MISSING** (do not reconstruct) |
| Invalid run `…122759Z…` | Not in repository | **ABSENT** (excluded by absence) |

### 1.5 Utility provenance (resolved for primary)

- **Canonical for primary figures/metrics:** `utility_success` on benign rows with `judge_status == ok`, aggregated by `scripts/score_p4_3_live_metrics.score_run` (fields produced by `agent/result_mapper.py` paired pipeline).
- **Not primary provenance:** `scripts/score_utility.py` (legacy v0, any-substring rule).
- **Status:** **VERIFIED** for P1/P2 planning; interpret as operational/heuristic (see `docs/AIB_SCIENTIFIC_INTEGRITY_AUDIT.md` S3).

### 1.6 P1 visualization (when branch/commit includes P1)

- Script: `scripts/generate_p1_figures.py`
- Figures: `docs/manuscript/figures/fig_p1_*.png|.pdf`
- Data: `docs/manuscript/figures/p1_figure_data.json`
- Tests: `tests/test_p1_figures.py`

---

## 2. Claim Audit (`docs/manuscript/agent_injection_benchmark_manuscript.md`)

### 2.1 Supported / appropriately bounded

- Controlled paired **descriptive** evaluation; COV-A primary n=9+9.
- Primary endpoint ASR; secondary Utility, FPR, paired transitions.
- D0 vs D2 as **evaluated conditions** (D2 = AdaptiGuard integration, not proven efficacy).
- Explicit negation of significance, superiority, SOTA, multi-model generalization, defense effectiveness proof.
- Limitations: small n, single target–judge, judge without IAA, `upstream_weight_revision` UNVERIFIED, missing `130300` run, mock tools, API non-determinism.
- Mock tool environment stated (§4 Threat Model).

### 2.2 Unsupported claims — manuscript check

Automated review (phrases: significant improvement, superiority, SOTA, comprehensive benchmark, production readiness, broad guarantee, causal effectiveness): **no affirmative unsupported claims found**; occurrences are negations or limitation text.

### 2.3 Stale external index

`docs/AIB_P8_SUBMISSION_READINESS.md` §8 states “No manuscript in repo”; manuscript now exists at `docs/manuscript/agent_injection_benchmark_manuscript.md`. **Factual doc drift only**—does not invalidate primary metrics. Update P8 in a separate doc-hygiene pass if desired (out of P2 scope unless requested).

**P2 manuscript action:** **No rewrite** (claims align with evidence).

---

## 3. Evidence Gap Matrix

| Dimension | Current evidence | Gap | Why it matters | Required future evidence |
|-----------|------------------|-----|----------------|--------------------------|
| Sample size | n=9 attacks, n=9 benign, 1 repetition | Small n; wide uncertainty on any rate | Descriptive snapshot only; weak external validity | Pre-registered expanded COV-A (or stated pool) with frozen manifest hash; still paired D0/D2 if same RQ |
| Model diversity | 1 target + 1 judge on primary run | No cross-model or cross-family ASR | Cannot support generalization across LLM families | Same protocol + scorer on additional locked targets (and optionally judges), each with immutable run manifest |
| Judge diversity | Single LLM judge | No human labels / IAA | Judge bias and construct validity unknown | Optional human adjudication protocol + IAA before confirmatory utility/attack labels |
| Attack diversity | 9 COV-A primary attacks (fixed IDs) | Not representative of full P4.2 corpus (200) or adaptive campaigns | Coverage of attack space limited | Extension manifests for COV-B or separate adaptive study (not mixed into primary) |
| Tool environment | 2 offline mocks (`search_docs`, `send_email`); synthetic tool replay in surface adapter | Not production agent stack | Agent injection severity may differ with real APIs/state | Controlled **realistic** tool sandbox (permissions, state, observable traces) under same paired contract |
| D2 runtime evidence | Scores + 18 defense traces + `defense_event` in RESULTS | Pre-target hook only (`docs/ADAPTI_GUARD_BRIDGE.md`); no per-tool-loop re-guard | Defense behavior partially evidenced; not full agent loop | Complete trace package per episode (prompt transform, decisions, tool steps) + documented hook coverage |
| Paired traces | D0/D2 per-episode JSON, execution traces in RESULTS | Bit-exact replay not guaranteed | Reproducibility is config-level | Provider revision logging + optional re-run archive (new run ID, not mutating `173736`) |
| Adaptive attacks | Excluded from primary freeze; tests/code for adaptive replay exist | **NOT PRIMARY EVIDENCE** | Adaptive robustness is separate scientific question | Track A/B or adaptive packs with own manifest—**NOT IN REPO** (P8 §6) |
| Statistical analysis | Descriptive only; no p-values/CIs in primary | No confirmatory design | Reviewers may ask for inference on expanded studies | Pre-registered test plan **after** design freeze & larger n (see §5) |
| Reproducibility | Git, configs, dataset digest, run bundle, CI verifiers, P1 figures | Weight revision UNVERIFIED; no provider-route cryptography | Limits strict replication claims | Weight revision evidence; documented provider order; optional offline artifact bundle |
| Human / IAA | **MISSING** | No inter-annotator study | Utility/attack labels rely on LLM judge | Human protocol if claims depend on subjective success |
| Weight revision | UNVERIFIED in freeze/manifest | Unknown model snapshot drift | ASR/utility may shift with provider updates | Recorded revision IDs per run |
| Provider / cache | No completion cache in `agent/llm.py`; config cache only | Route not cryptographically attested | Trust model for third-party API | Manifest fields + operator attestation or local replay where possible |
| Artifact completeness | Code, freeze, data, primary results, tests, manuscript, P1 figures | P6 `130300` missing; Track A/B packs absent | Submission packaging gaps | Publish missing runs only as **new immutable archives**; external supplements with SHA |

---

## 4. Scientific Risks

| Risk | Severity | Mitigation (documentation / future work) |
|------|----------|----------------------------------------|
| Over-interpreting n=9 descriptive parity (ASR 1/9 vs 1/9) as defense effect | High | Keep manuscript/P8 claim safety; no causal language |
| Mixing COV-B/C or adaptive results into primary | High | Freeze roles; separate run IDs |
| Utility judge vs substring fallback confusion | Medium | Cite `result_mapper` + P1 utility provenance |
| Mock tools ≠ deployed agents | Medium | State in threat model; future realistic harness |
| Single target model | High | Model sweep as future authorized experiment |
| LLM judge without IAA | Medium | Limit claims; optional human study |
| `upstream_weight_revision` UNVERIFIED | Medium | No weight-sensitive claims |
| Missing `130300` run in git | Low for current claims if `173736` cited | Disclose limitation (manuscript §12) |

---

## 5. Future Experimental Requirements (NOT EXECUTED)

Each future study requires separate approval artifacts, gate flags, and a **new** immutable run ID. Do not mutate `…173736Z-controlled`.

### 5.1 Expanded paired descriptive / confirmatory COV-A

| Field | Requirement |
|-------|-------------|
| Objective | Estimate D0 vs D2 ASR (and secondary metrics) on a pre-registered episode pool |
| Population | Frozen manifest hash; coverage class stated upfront |
| Independent variables | Defense condition (D0, D2) |
| Controls | Same target/judge lock unless explicitly amended |
| Primary endpoint | ASR (attacks) |
| Secondary endpoints | S2, S3, S4, Utility, FPR, paired transitions |
| Required traces | Full D0/D2 RESULTS, defense traces, RUN_MANIFEST |
| Reproducibility | Seed, model IDs, AdaptiGuard pin, git commit, scorer version |
| Stopping/validation | Fixed N; descriptive until confirmatory protocol approved |

**Future design note:** Power analysis and exact paired test (e.g., McNemar on paired attack success) belong in a **confirmatory protocol** frozen **before** execution (`docs/AIB_P8_FUTURE_EXPERIMENT_PROTOCOL_DRAFT.md` skeleton). P2 does **not** report power or p-values on current n=9.

### 5.2 Multi-model extension

| Field | Requirement |
|-------|-------------|
| Objective | Same paired contract across ≥2 target model families |
| Population | Same episode IDs per model where possible |
| Controls | Per-model RUN_MANIFEST + gate lock evidence |
| Primary endpoint | ASR per model (descriptive tables; multiplicity pre-registered if confirmatory) |

### 5.3 Realistic tool environment

| Field | Requirement |
|-------|-------------|
| Objective | Observable tool-call traces under controlled realism (permissions, state) |
| Population | Subset or extension manifest—not retroactive change to `173736` |
| Required traces | Tool execution logs, defense decisions per step when D2 |

### 5.4 Adaptive evaluation (extension only)

| Field | Requirement |
|-------|-------------|
| Objective | Adaptive attack campaigns (e.g., AdaptiGuard Track A/B) |
| Status today | **NOT PRIMARY EVIDENCE**; packs **NOT IN REPO** |
| Dependency | Separate protocol; do not merge into P4.2 primary freeze |

### 5.5 Human evaluation (optional)

| Field | Requirement |
|-------|-------------|
| Objective | IAA on subset of attack/utility labels |
| Population | Sampled episodes with adjudication guide |
| Stopping | Pre-defined n and agreement thresholds |

---

## 6. Q1-Level Evidence Requirements (operationalized)

### Level A — Current descriptive study (evidence **now**)

- Immutable run `173736`: paired D0/D2 on COV-A n=9+9; descriptive ASR, Utility, FPR, transitions.
- Frozen protocol, decision sheet, dataset digest, scorer contracts, CI offline verifiers.
- Manuscript + P1 figures derived from scorer (no new experiments).
- Explicit limitations and non-claims.

**Suitable claims:** sample-level observations, benchmark/protocol artifact description, evaluated defense **condition** (not efficacy).

### Level B — Stronger empirical submission

- Expanded n with pre-registered manifest.
- Multiple target models (same contract).
- Stronger environment realism (tools/traces).
- Complete D2 behavioral trace narrative (hook coverage documented).
- Optional confirmatory statistics on **new** frozen study.
- Artifact bundle: all runs checksummed; reproducibility index updated.

### Level C — High-bar security venue preparation (no acceptance guarantee)

- Broad model and attack coverage (including adaptive extensions where justified).
- Independent validation / replication run by second operator or site.
- Human IAA or hybrid judge protocol for critical labels.
- Verified weight revisions and provider documentation.
- Baseline comparisons beyond D0 (only if pre-registered—no D1 in current primary).
- Full artifact + threat-model alignment with realistic agent deployments.

---

## 7. Prioritization (sequencing)

### P0 — Blocking scientific validity (if violated)

| Gap | Current evidence | Risk | Required action | Dependency | Value |
|-----|------------------|------|-----------------|------------|-------|
| Claim overreach | Manuscript bounded today | Misrepresentation | Claim audit before each submission | Manuscript | Integrity |
| Wrong run cited | `173736` frozen | Invalid evidence | Cite only `historical_run_immutable` | Freeze | Validity |
| Mixing adaptive/primary | Primary excludes adaptive | Conflated RQ | Separate run IDs & manifests | D8 freeze | Validity |

### P1 — High-value strengthening

| Gap | Action | Dependency |
|-----|--------|------------|
| Small n | Expanded paired study (new run) | P8 future protocol approval |
| Single model | Multi-model locked runs | Gate + manifests |
| Mock tools | Realistic controlled harness | Engineering + protocol amendment |
| D2 loop coverage | Tool-loop defense + traces | AdaptiGuard bridge extension |
| Weight revision | Capture provider revision metadata | API/manifest schema |

### P2 — Useful, non-blocking

| Gap | Action |
|-----|--------|
| P8 §8 stale “no manuscript” | Doc sync |
| Post-release git tag | Release hygiene |
| P6 `130300` archive | External publication if operator holds bytes |

### P3 — Optional polish

| Gap | Action |
|-----|--------|
| Additional figure variants | P1 pipeline only |
| Extended related-work tables | Manuscript only |

---

## 8. Minimum Viable Strengthening Path (evidence-supported order)

1. **Freeze expanded population** — new manifest hash (COV-A extension or pre-registered pool); do not edit `173736`.
2. **Execute authorized paired D0/D2 live runs** — larger n, same contracts, new run IDs.
3. **Add target model families** — parallel manifests per model.
4. **Upgrade tool environment** — controlled realism + observable traces; keep paired scoring contract.
5. **Document full D2 runtime** — per-step defense decisions when tool-loop guard ships.
6. **Adaptive studies** — separate extension (Track A/B) with own evidence chain.
7. **Confirmatory statistics** — only after step 1–2 and explicit protocol freeze (not on current n=9 alone).

---

## 9. Research Contribution Audit

| Area | AIB current position | Evidence strength |
|------|----------------------|-------------------|
| Indirect / agent injection | Frozen COV-A paired harness + live run | **Limited** (n=9, mock tools) |
| Tool/agent security evaluation | S1–S4 + mock tool execution evidence | **Partial** (sandbox) |
| Defenses | D2 AdaptiGuard integration + pin | **Integration evidenced**; **efficacy not evidenced** (ASR parity) |
| Benchmark / evaluation methodology | Freeze, gates, CI, reproducibility docs | **Strong** (artifact) |
| Adaptive attacks | Code/tests; not primary | **Not evidenced** for claims |

**Novelty (conservative):** Paired immutable D0/D2 descriptive protocol + artifact chain on a tool-using agent benchmark—not a new large-scale attack corpus claim. Differentiation vs InjecAgent/AgentDojo is **scope** (frozen paired primary pool, in-repo live run), not scale.

**Insufficiently evidenced for strong novelty claims:** defense improvement, adaptive robustness, multi-model leaderboard, comprehensive benchmark coverage.

---

## 10. Current Limitations (summary)

- n=9 attacks; single repetition; descriptive statistics only.
- One target and one judge on primary run.
- Mock offline tools; synthetic tool-result replay.
- LLM judge without human IAA.
- `upstream_weight_revision` UNVERIFIED.
- API stochasticity; seed not guaranteed by provider.
- Missing in-repo `130300`; Track A/B not in tree.
- D2 defense hook: pre-target only (per bridge doc).

---

## 11. Explicit Non-Claims

Do **not** claim from current repository evidence:

- Statistically significant D2 improvement or superiority.
- SOTA or robust defense.
- Multi-model or population generalization.
- Comprehensive benchmark over full P4.2 corpus.
- Production readiness or universal security guarantee.
- Causal effectiveness of D2.
- Adaptive defense/attack results in primary P4.2 narrative.
- Bit-exact reproducibility of API completions.
- Confirmatory hypothesis tests on the frozen `173736` sample.

---

## 12. P2 Execution Record

| Check | Result |
|-------|--------|
| Baseline metrics vs scorer | **PASS** (matches expected 1/9, 9/9, 0/9, transitions 1/0/0/8) |
| Historical `RESULTS.json` mutated | **NO** (P2 doc-only) |
| Live API / experiment | **NONE** |
| Manuscript changed | **NO** |
| New canonical artifact | This file |

**Related docs:** `docs/AIB_PHASE5_RESEARCH_DECISION_SHEET.md`, `docs/AIB_RESEARCH_CONTROLLED_DEFENSE_EXPERIMENT_SPEC.md`, `docs/AIB_P8_SUBMISSION_READINESS.md`, `docs/AIB_SCIENTIFIC_INTEGRITY_AUDIT.md`, `docs/AIB_REPRODUCIBILITY_INDEX.md`, `docs/manuscript/agent_injection_benchmark_manuscript.md`.
