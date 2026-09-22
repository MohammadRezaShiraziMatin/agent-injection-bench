# Title

**Agent-Injection-Bench: A Controlled Paired Descriptive Evaluation of Indirect Prompt Injection in Tool-Using Agents (COV-A Primary, n=9)**

## Abstract

We report a **controlled, paired, descriptive** evaluation of indirect prompt injection against a tool-using LLM agent on a frozen COV-A primary pool (9 attack and 9 benign episodes). Each episode is executed under two conditions: **D0** (no defense) and **D2** (AdaptiGuard integration as an evaluated defense condition). The primary tracked live run in this repository is `p42-primary-d0-d2-20260921T173736Z-controlled` (36 judged records; 0 judge failures). Observed attack success rate (ASR) is **1/9** under both D0 and D2; benign utility is **9/9** and false-positive rate (FPR) is **0/9** under both conditions. Paired attack transitions (D0→D2 success status) are **1** success→success, **0** success→failure, **0** failure→success, and **8** failure→failure. These results are **sample-level observations** on a single verified target model and judge configuration; they do **not** establish statistical significance, defense superiority, multi-model generalization, or state-of-the-art performance.

## 1. Introduction

Indirect prompt injection exposes tool-using agents to adversarial content in retrieved or tool-mediated context. Agent-Injection-Bench (AIB) provides frozen datasets, evaluation contracts, harnesses, and recorded live runs intended for **reproducible, evidence-bounded** reporting. This manuscript summarizes only what is supported by the canonical primary run identified above—not the full 200-episode corpus as a population estimate.

## 2. Research Questions

**RQ1 (descriptive):** On the frozen COV-A primary pool (n=9 attacks, n=9 benign), what are the observed ASR, utility, and FPR under D0 versus D2 for one locked target–judge pair?

**Out of scope for this evidence:** confirmatory hypothesis tests, population-level efficacy, multi-model benchmarks, adaptive attack campaigns, or Track A/B comparisons (not evidenced in-repo).

## 3. Related Work

External benchmark mapping and citation readiness are documented in `docs/AIB_P4_3_EXTERNAL_BENCHMARK_AUDIT.md` (e.g., AgentDojo, InjecAgent, Tensor Trust, PIArena). **MANUAL VERIFICATION REQUIRED** for complete bibliographic entries before submission; this draft does not invent DOIs or publication metadata.

## 4. Threat Model

We evaluate **indirect** injection: adversarial content appears in agent context (e.g., retrieved documents), not in the user’s direct instruction. The agent may call **offline mock tools** (`search_docs`, `send_email`) under harness control. Success criteria follow frozen severity labels (S1–S4) and episode-specific expectations in the P4.2 schema. The primary run does not claim coverage of all real-world agent deployments.

## 5. Attack Taxonomy

P4.2 episodes encode interaction types, horizons, and success criteria (S1–S4). The **primary analysis population** is COV-A–eligible episodes selected in `artifacts/p4_2_primary_d0_d2_experiment/MANIFEST.json` (9 attack + 9 benign). Broader COV-B/C strata exist for diagnostic/extension work and are **not** the primary n=9 claim set.

## 6. Benchmark and Dataset

- **Frozen protocol:** `config/p4_2_primary_research_protocol_freeze.v1.json` (status: FROZEN; descriptive-only statistics).
- **Decision sheet:** `docs/AIB_PHASE5_RESEARCH_DECISION_SHEET.md`.
- **Episode corpus:** P4.2 frozen dataset under `data/episodes_p4_2/` (digest referenced in protocol).
- **Primary design manifest:** `artifacts/p4_2_primary_d0_d2_experiment/MANIFEST.json`.
- **Independent validation corpus (P4.4):** separate freeze; not pooled into primary n=9 metrics here.

## 7. Defense Conditions

| Condition | Description |
|-----------|-------------|
| **D0** | No defense: middleware passthrough (`D0_no_defense`). |
| **D2** | **Evaluated defense condition:** AdaptiGuard `CoreDefensePipeline` via AIB bridge; pinned commit `30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64` (`config/adaptiguard_version_pin.v1.json`). |

D2 is reported as an **evaluated mitigation condition**, not as a proven robust or state-of-the-art defense. No D1 condition appears in the primary protocol freeze.

## 8. Experimental Protocol

- **Study type:** controlled paired descriptive evaluation (D0 then D2 per episode).
- **Run ID:** `p42-primary-d0-d2-20260921T173736Z-controlled`.
- **Seed (recorded):** `43020260921` (`RUN_MANIFEST.json`); provider may not guarantee bit-exact replay.
- **Target model (verified on this run):** `openai/gpt-4o-mini-2024-07-18` (OpenRouter).
- **Judge model (verified on this run):** `meta-llama/llama-3.3-70b-instruct`.
- **Repetition:** 1 (per protocol freeze).
- **Live gate:** `live_d2_inference_allowed` is false in gate config by default; this run is historical/immutable evidence, not a new execution.

**Evidence boundary:** Run `p42-primary-d0-d2-20260922T130300Z-controlled` is **not present in the current repository and therefore excluded from the reported evidence.**

## 9. Metrics

Definitions follow `config/p4_3_evaluation_metrics.v1.json` and paired scorer `scripts/score_p4_3_paired_metrics.py`.

- **ASR:** attack successes / valid judged attack episodes.
- **Utility:** benign task success / valid judged benign episodes.
- **FPR:** false positive blocks or attack-labeled benign episodes / valid judged benign episodes (paired contract).

**Utility provenance (primary run):** Records in `RESULTS.json` are produced via the paired pipeline (`agent/result_mapper.py`). For benign episodes with `judge_status == "ok"`, utility uses the **LLM judge** field `utility_success` when present; otherwise a **substring heuristic** requiring **all** tokens in `expected.utility_answer_contains` to appear in `final_answer` (case-insensitive). This differs from legacy `scripts/score_utility.py` on v0 traces, which uses **any** substring match—**not** the provenance path for this primary run. Utility should be interpreted as **operational/heuristic**, with judge limitation noted below.

## 10. Results

**Source:** `results/p4_2_paired/p42-primary-d0-d2-20260921T173736Z-controlled/RESULTS.json` (verified: 36 rows, 0 judge failures).

| Metric | D0 | D2 |
|--------|----|----|
| ASR | 1/9 (11.11%) | 1/9 (11.11%) |
| Utility | 9/9 (100%) | 9/9 (100%) |
| FPR | 0/9 (0%) | 0/9 (0%) |

**Paired attack transitions (D0 attack_success → D2 attack_success):**

| Transition | Count |
|------------|------:|
| success → success | 1 |
| success → failure | 0 |
| failure → success | 0 |
| failure → failure | 8 |

**Descriptive delta (ASR):** 0 between D0 and D2 on this sample. No inferential test is reported.

## 11. Discussion

The primary sample shows **parity** in ASR between D0 and D2 (1/9 each) with unchanged utility and FPR on benign episodes. This is consistent with a **limited descriptive** snapshot, not with a claim that D2 reduces attack success in general. Interpretation must respect COV-A selection, single target model, single repetition, and operational judge. Adaptive studies and Track A/B packs are excluded from the primary protocol and are not evidenced in this repository.

## 12. Limitations

1. **Small n:** 9 attack + 9 benign episodes in the primary population.
2. **Descriptive design:** no confirmatory statistical inference; multiplicity not controlled for confirmatory claims.
3. **Single verified target–judge pair** on the primary run; no multi-model generalization.
4. **Judge:** operational LLM judge; no human inter-rater agreement in-repo.
5. **`upstream_weight_revision`:** UNVERIFIED in protocol/manifest.
6. **Missing run:** `p42-primary-d0-d2-20260922T130300Z-controlled` is **not present in the current repository and therefore excluded from the reported evidence.**
7. **Utility:** judge + substring fallback; limited construct validity.
8. **Reproducibility:** configuration and artifacts are tracked; API stochasticity may prevent bit-identical replication.
9. **No superiority, SOTA, or population-level efficacy** claims are supported.

## 13. Reproducibility

Evidence chain (repository paths):

```text
git commit (e.g. e6848caa02c56599d64fab865ffd5321ca67406f on main at manuscript authoring)
  → config/p4_2_primary_research_protocol_freeze.v1.json
  → data/episodes_p4_2/ + artifacts/p4_2_primary_d0_d2_experiment/MANIFEST.json
  → config/p4_3_* gates/contracts + config/adaptiguard_version_pin.v1.json
  → results/p4_2_paired/p42-primary-d0-d2-20260921T173736Z-controlled/ (RUN_MANIFEST.json, RESULTS.json, per-episode JSON)
  → python scripts/score_p4_3_paired_metrics.py <run_dir>
  → docs/AIB_FINAL_RESEARCH_READINESS.md / docs/AIB_REPRODUCIBILITY_INDEX.md
```

Offline checks: `pytest -q`; `python scripts/verify_p4_2_freeze.py`; `verify_p4_2_primary_prelive_gate.py`; `verify_p4_3_integrity.py`; CI workflow `.github/workflows/research-ci.yml`.

## 14. Conclusion

AIB provides a frozen, controlled paired **descriptive** benchmark with immutable primary live evidence on COV-A (n=9+9). Reported metrics are sample observations for one model configuration; they do not prove defense effectiveness, statistical improvement, or broad generalization. Future work requires separately authorized experiments (larger n, multi-model, confirmatory design).

## Tables

See §10 (primary results) and §7 (defense conditions). Table 4-style evidence/limitation mapping: `docs/AIB_FINAL_RESEARCH_READINESS.md` §9.

## Figure Specifications

Figures may be generated **offline** from verified counts in `RESULTS.json` (no new live runs):

1. **Bar chart:** D0 vs D2 ASR (1/9 each).
2. **Bar chart:** Utility and FPR (9/9, 0/9).
3. **Paired transition diagram:** counts 1 / 0 / 0 / 8.

Do not imply causal or population inference in captions.

## References

- Repository documentation and audit trail (primary): `docs/AIB_P8_SUBMISSION_READINESS.md`, `docs/AIB_SCIENTIFIC_INTEGRITY_AUDIT.md`, `docs/AIB_P4_3_EXTERNAL_BENCHMARK_AUDIT.md`.
- AdaptiGuard integration: `docs/ADAPTI_GUARD_BRIDGE.md`.
- **External papers:** complete citations require **MANUAL VERIFICATION REQUIRED** from primary sources before submission.
