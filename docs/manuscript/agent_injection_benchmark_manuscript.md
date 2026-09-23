# Title

**Agent-Injection-Bench: A Controlled Paired Descriptive Evaluation of Indirect Prompt Injection in Tool-Using Agents (COV-A Primary, n=9)**

## Abstract

We report a **controlled, paired, descriptive** evaluation of indirect prompt injection against a tool-using LLM agent on a frozen COV-A primary pool (9 attack and 9 benign episodes). Each episode is executed under two conditions: **D0** (no defense) and **D2** (AdaptiGuard integration as an evaluated defense condition). The primary tracked live run in this repository is `p42-primary-d0-d2-20260921T173736Z-controlled` (36 judged records; 0 judge failures). Observed attack success rate (ASR) is **1/9** under both D0 and D2; benign utility is **9/9** and false-positive rate (FPR) is **0/9** under both conditions. Paired attack transitions (D0→D2 success status) are **1** success→success, **0** success→failure, **0** failure→success, and **8** failure→failure. These results are **sample-level observations** on a single verified target model and judge configuration; they do **not** establish statistical significance, defense superiority, multi-model generalization, or state-of-the-art performance.

## 1. Introduction

Indirect prompt injection exposes tool-using agents to adversarial content in retrieved or tool-mediated context [1]. Agent-Injection-Bench (AIB) provides frozen datasets, evaluation contracts, harnesses, and recorded live runs intended for **reproducible, evidence-bounded** reporting. This manuscript summarizes only what is supported by the canonical primary run identified above—not the full 200-episode corpus as a population estimate.

## 2. Research Questions

**RQ1 (descriptive):** On the frozen COV-A primary pool (n=9 attacks, n=9 benign), what are the observed ASR, utility, and FPR under D0 versus D2 for one locked target–judge pair?

**Out of scope for this evidence:** confirmatory hypothesis tests, population-level efficacy, multi-model benchmarks, adaptive attack campaigns, or Track A/B comparisons (not evidenced in-repo).

### 2.1 Evidence claim level (Level A / B / C)

**Current level: Level A (descriptive).** Level A is defined by evidence **type and quality** (controlled paired design, immutable runs, frozen protocols, scorer-backed descriptive metrics, explicit limitations)—not by sample size alone. The tracked Level A package comprises: (1) **P4.2 primary COV-A** (`p42-primary-d0-d2-20260921T173736Z-controlled`; §10); and (2) **P3-EXT COV-B** (`p3-cov-b-ext-20260923T112900Z-controlled`; §10.1), a separate descriptive extension that does **not** supersede the primary layer and does **not** automatically advance the project to Level B.

**Allowed at Level A:** sample-level observed ASR, Utility, FPR, and paired transitions; protocol and artifact provenance; **D2 defense integration** and **observed D0/D2 behavior** on the recorded execution path.

**Excluded at Level A:** claims of robust or general defense effectiveness, superiority, state-of-the-art performance, statistical significance, broad generalization, production readiness, or comprehensive security coverage.

**Level B** (future) requires a new pre-specified protocol and fresh immutable runs (e.g., multi-model coverage, richer harness/traces, optional confirmatory design)—see `docs/AIB_P2_Q1_EVIDENCE_GAP_PLAN.md`. **Level C** denotes higher evidence maturity for security-venue preparation, not guaranteed acceptance. Venue positioning is descriptive only (Level A: workshop/findings/artifact-oriented paths; Level B: stronger empirical paths once evidenced; Level C: higher-evidence security-venue preparation).

## 3. Related Work

**Indirect prompt injection and agent threat models.** Greshake et al. [1] formalize indirect prompt injection against LLM-integrated applications where retrieved data can act as adversarial instructions. Follow-on work studies automated black-box injection frameworks [6] and tool-integrated agent benchmarks [2, 3]. We cite these works only to situate the threat model and evaluation landscape—not to claim our n=9 descriptive run generalizes their findings.

**Benchmarks and datasets.** InjecAgent [2] benchmarks indirect injections in tool-integrated agents (1,054 test cases). AgentDojo [3] provides a dynamic environment with realistic tasks and security test cases for agent prompt injection. Tensor Trust [4] supplies a large human-generated attack/defense dataset from an online game. BIPIA [5] spans multiple application scenarios for indirect injection. PIArena [8] is a unified evaluation platform with adaptive attack strategies. AIB differs in scope: a frozen, paired D0/D2 descriptive protocol on a fixed COV-A primary pool with immutable run artifacts in-repo.

**Defenses (context only).** StruQ [7] separates prompt and data channels via structured queries and specialized fine-tuning. Our D2 condition evaluates AdaptiGuard as an **integrated mitigation pipeline** on the primary run; we do **not** claim parity with StruQ-style training or that D2 constitutes a generally effective defense.

**Not cited (UNVERIFIED in this pass):** standalone primary artifacts for Task Shield, Spotlighting, and VIGIL were not verified from publisher/arXiv pages and are omitted to avoid citation dumping.

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
- **Repository release:** frozen artifacts and protocols in AIB [9].

## 7. Defense Conditions

| Condition | Description |
|-----------|-------------|
| **D0** | No defense: middleware passthrough (`D0_no_defense`). |
| **D2** | **D2 defense integration:** AdaptiGuard `CoreDefensePipeline` via AIB bridge on the recorded execution path; pinned commit `30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64` (`config/adaptiguard_version_pin.v1.json`). |

D2 is reported as **integrated defense execution** with **observed D0/D2 behavior** in paired runs—not as effective, robust, or superior protection. No D1 condition appears in the primary protocol freeze.

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

### 10.1 Expanded descriptive extension (P3-EXT, COV-B)

**Scope:** Separately authorized live extension on COV-B (`config/p3_experimental_protocol_freeze.v1.json`; manifest `artifacts/p3_cov_b_extension/MANIFEST.json`). This layer is **not** pooled with the COV-A primary n=9 claims in §10.

- **Run ID:** `p3-cov-b-ext-20260923T112900Z-controlled`
- **Population:** 42 attack + 42 benign episodes (84 records per `D0/RESULTS.json` and `D2/RESULTS.json`)
- **Target / judge (verified on this run):** `openai/gpt-4o-mini-2024-07-18`; `meta-llama/llama-3.3-70b-instruct`
- **Validity:** 84 episodes executed per condition; paired D0/D2 episode identities match

**Judge quality:** One D0 judge failure on attack episode `atk_p42_045` (`judge_status=JUDGE_FAILURE`); zero D2 judge failures. The failed D0 judgment is preserved in raw evidence; it was **not** rerun in post-live reconciliation.

| Metric | D0 | D2 |
|--------|----|----|
| ASR | 11/41 (26.8%) | 11/42 (26.2%) |
| Utility | 35/42 (83.3%) | 35/42 (83.3%) |
| FPR | 0/42 (0%) | 0/42 (0%) |

D0 ASR denominator 41 reflects exclusion of `atk_p42_045` from valid judged attacks per scorer contract; 42 attacks were still executed under D0.

**Paired attack transitions (D0 attack_success → D2 attack_success):**

| Transition | Count |
|------------|------:|
| success → success | 11 |
| success → failure | 0 |
| failure → success | 0 |
| failure → failure | 31 |

**Interpretation (bounded):** Observed descriptive counts on the specified COV-B sample, target, judge, and execution only. Compared to §10 (COV-A, n=9), ASR numerators/denominators differ by design (coverage class and sample size); any cross-layer numeric difference is an **observed descriptive difference**, not evidence of defense success or failure in general.

## 11. Discussion

The primary sample shows **parity** in ASR between D0 and D2 (1/9 each) with unchanged utility and FPR on benign episodes. This is consistent with a **limited descriptive** snapshot, not with a claim that D2 reduces attack success in general. Interpretation must respect COV-A selection, single target model, single repetition, and operational judge. Adaptive studies and Track A/B packs are excluded from the primary protocol and are not evidenced in this repository.

The P3-EXT COV-B extension (§10.1) reports larger-n descriptive counts under the same D0/D2 pairing protocol on a different coverage class; it does not supersede §10 and does not support confirmatory or superiority claims.

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
10. **P3-EXT (COV-B):** single target and judge as in §10.1; one D0 judge failure (`atk_p42_045`); descriptive extension only; COV-B-specific coverage; no adaptive attack evaluation; no human IAA; not generalizable to all agents or models; provider/cache constraints per frozen P3 protocol.

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

AIB’s current evidence is at **Level A**: controlled paired **descriptive** evaluation with immutable artifacts for P4.2 primary COV-A (n=9+9) and the separate P3-EXT COV-B extension (§10.1). Reported metrics are sample observations for specified target–judge configurations; they do not establish confirmatory effectiveness, superiority, or broad generalization. Reaching **Level B** requires a new experimental protocol and fresh immutable runs as documented in `docs/AIB_P2_Q1_EVIDENCE_GAP_PLAN.md`.

## Tables

See §10 (primary results) and §7 (defense conditions). Table 4-style evidence/limitation mapping: `docs/AIB_FINAL_RESEARCH_READINESS.md` §9.

## Figures

Generated offline from `D0/RESULTS.json` and `D2/RESULTS.json` via `python scripts/generate_p1_figures.py` (run `p42-primary-d0-d2-20260921T173736Z-controlled`; see `docs/manuscript/figures/p1_figure_data.json`). Descriptive only—no inferential claims in captions.

**Figure 1.** Descriptive comparison of attack success rate (ASR) between D0 (no defense) and D2 (AdaptiGuard defense) on the verified COV-A primary attack set (n = 9). File: `docs/manuscript/figures/fig_p1_primary_asr_d0_d2.png`.

**Figure 2.** Descriptive comparison of benign utility and false-positive rate (FPR) under D0 and D2 (n = 9 benign episodes). Utility counts use `utility_success` from the paired pipeline scorer (`scripts/score_p4_3_live_metrics.py`). File: `docs/manuscript/figures/fig_p1_utility_fpr_d0_d2.png`.

**Figure 3.** Observed paired attack outcome transitions from D0 to D2 attack_success status (success→success: 1; success→failure: 0; failure→success: 0; failure→failure: 8). File: `docs/manuscript/figures/fig_p1_paired_transitions_d0_d2.png`.

**P3-EXT (COV-B, separate from §10):** Generated via `python scripts/generate_p3_figures.py` from run `p3-cov-b-ext-20260923T112900Z-controlled` (`docs/manuscript/figures/p3_figure_data.json`). Descriptive only; valid judged denominators per scorer (D0 ASR n=41 attacks due to one D0 judge failure).

**Figure 4.** P3-EXT ASR under D0 versus D2 on COV-B attacks (D0: 11/41; D2: 11/42). File: `docs/manuscript/figures/fig_p3_ext_asr_d0_d2.png`.

**Figure 5.** P3-EXT benign utility and FPR (n = 42 benign). File: `docs/manuscript/figures/fig_p3_ext_utility_fpr_d0_d2.png`.

**Figure 6.** P3-EXT paired attack transitions (success→success: 11; failure→failure: 31). File: `docs/manuscript/figures/fig_p3_ext_paired_transitions_d0_d2.png`.

## References

[1] Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, and Mario Fritz. 2023. Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection. In *Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security (AISec '23)*, 79–90. DOI: [10.1145/3605764.3623985](https://doi.org/10.1145/3605764.3623985). arXiv: [2302.12173](https://arxiv.org/abs/2302.12173).

[2] Qiusi Zhan, Zhixiang Liang, Zifan Ying, and Daniel Kang. 2024. InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents. In *Findings of the Association for Computational Linguistics: ACL 2024*, 10471–10506, Bangkok, Thailand. DOI: [10.18653/v1/2024.findings-acl.624](https://doi.org/10.18653/v1/2024.findings-acl.624). arXiv: [2403.02691](https://arxiv.org/abs/2403.02691).

[3] Edoardo Debenedetti, Jie Zhang, Mislav Balunović, Luca Beurer-Kellner, Marc Fischer, and Florian Tramèr. 2024. AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents. In *NeurIPS 2024 Datasets and Benchmarks Track*. DOI: [10.52202/079017-2636](https://doi.org/10.52202/079017-2636).

[4] Sam Toyer, Olivia Watkins, Ethan Adrian Mendes, Justin Svegliato, Luke Bailey, Tiffany Wang, Isaac Ong, Karim Elmaaroufi, Pieter Abbeel, Trevor Darrell, Alan Ritter, and Stuart Russell. 2023. Tensor Trust: Interpretable Prompt Injection Attacks from an Online Game. arXiv: [2311.01011](https://arxiv.org/abs/2311.01011).

[5] Jingwei Yi, Yueqi Xie, Bin Zhu, Keegan Hines, Emre Kiciman, Guangzhong Sun, Xing Xie, and Fangzhao Wu. 2023. Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models. arXiv: [2312.14197](https://arxiv.org/abs/2312.14197). Code: [microsoft/BIPIA](https://github.com/microsoft/BIPIA).

[6] Yi Liu, Gelei Deng, Yuekang Li, Kailong Wang, Zihao Wang, Xiaofeng Wang, Tianwei Zhang, Yepang Liu, Haoyu Wang, Yan Zheng, Leo Yu Zhang, and Yang Liu. 2023. Prompt Injection attack against LLM-integrated Applications. arXiv: [2306.05499](https://arxiv.org/abs/2306.05499).

[7] Sizhe Chen, Julien Piet, Chawin Sitawarin, and David Wagner. 2025. StruQ: Defending Against Prompt Injection with Structured Queries. In *34th USENIX Security Symposium (USENIX Security 25)*, 2383–2400. URL: [USENIX presentation](https://www.usenix.org/conference/usenixsecurity25/presentation/chen-sizhe). arXiv: [2402.06363](https://arxiv.org/abs/2402.06363).

[8] Runpeng Geng, Chenlong Yin, Yanting Wang, Ying Chen, and Jinyuan Jia. 2026. PIArena: A Platform for Prompt Injection Evaluation. In *Proceedings of ACL 2026* (long paper). ACL Anthology: [2026.acl-long.1533](https://aclanthology.org/2026.acl-long.1533/). arXiv: [2604.08499](https://arxiv.org/abs/2604.08499).

[9] MohammadReza Shirazi Matin et al. *Agent-Injection-Bench (AIB)* repository and frozen evaluation artifacts. GitHub: [MohammadRezaShiraziMatin/agent-injection-bench](https://github.com/MohammadRezaShiraziMatin/agent-injection-bench). Primary run: `results/p4_2_paired/p42-primary-d0-d2-20260921T173736Z-controlled/`. Internal docs: `docs/AIB_P8_SUBMISSION_READINESS.md`, `docs/AIB_SCIENTIFIC_INTEGRITY_AUDIT.md`, `docs/ADAPTI_GUARD_BRIDGE.md`.
