# AIB — Scientific & engineering integrity audit (post-release)

**Audit date:** 2026-09-22 (UTC)  
**Canonical commit:** `main` @ release merge + `docs/AIB_FINAL_RESEARCH_READINESS.md`  
**Primary tracked run:** `p42-primary-d0-d2-20260921T173736Z-controlled`

## Evidence matrix

| Claim | Evidence | File / run | Run ID | Status |
|-------|----------|------------|--------|--------|
| Primary ASR (D0/D2) | `RESULTS.json` + scorer | `results/p4_2_paired/…173736Z…/` | `…173736Z…` | **VERIFIED** (1/9 each) |
| Utility (benign) | Judge + substring fallback | same | same | **PARTIAL / LIMITED** (see S3) |
| FPR | Scorer contract | same | same | **VERIFIED** (0/9 each) |
| Target model evaluated | `RUN_MANIFEST.json` | same | same | **VERIFIED** (`openai/gpt-4o-mini-2024-07-18`) |
| Judge model | manifest + gate | same | same | **VERIFIED** (`meta-llama/llama-3.3-70b-instruct`) |
| D2 defense (AdaptiGuard) | Integration + pin | `config/adaptiguard_version_pin.v1.json` | same | **VERIFIED** (pinned SHA; not efficacy claim) |
| D0 baseline | No defense middleware | `agent/defense/middleware.py` | same | **VERIFIED** |
| Reproducibility (bit-exact) | Seed recorded | manifest `seed: 43020260921` | same | **PARTIAL / LIMITED** (see S5) |
| Multi-model ASR | — | — | — | **NOT VERIFIED** (single target in primary) |
| Adaptive primary | Protocol excludes | freeze `adaptive_scope` | — | **NOT VERIFIED** (excluded) |
| P6 re-run `130300` | — | — | `…130300Z…` | **NOT VERIFIED** (not in repo) |

## S1 — Sample size

| Population | n (primary) | Role |
|------------|-------------|------|
| Attack (COV-A primary) | 9 | Primary ASR denominator |
| Benign (matched) | 9 | Utility / FPR |
| P4.2 corpus | 200 | Dataset; not all in primary run |
| P4.3 live paired (historical) | 4 attacks (COV-C) | Diagnostic / separate reports |

**Conclusion:** n=9 supports **descriptive** paired comparison only. Confirmatory / population / general claims are **UNSUPPORTED** (P8 §3, §9).

## S2 — Model coverage

- **Live-evaluated (primary):** one target + one judge per `RUN_MANIFEST.json`.
- **Configured elsewhere:** gate/catalog JSON; not equivalent to evaluated unless run manifest records execution.
- **Fallback:** `OPENROUTER_ALLOW_FALLBACKS` defaults false in `agent/config.py`; manifest should be checked per run.

## S3 — Utility metric

**Implementation (paired / live path):** `agent/result_mapper.py`

1. If `judge_status == "ok"` and benign: prefer `utility_success` from **LLM judge** (`agent/judge.py`).
2. If judge omits utility: **`_utility_substrings`** — requires **all** tokens in `expected.utility_answer_contains` to appear in `final_answer` (case-insensitive).

**Legacy v0 script:** `scripts/score_utility.py` uses **any** substring match on traces — **not identical** to paired mapper; do not mix provenance.

**Limitations:** substring heuristic → false positives/negatives; judge is operational, not human IAA (P8 §5).

## S4 — Defense conditions (terminology)

Primary protocol conditions: **D0** (no defense) and **D2** (AdaptiGuard via `apply_adaptiguard`). There is **no D1** in `p4_2_primary_research_protocol_freeze.v1.json`.

- **D0:** passthrough (`D0_no_defense`).
- **D2:** external AdaptiGuard pipeline — **mitigation condition**, not “strong/SOTA defense.”
- Do not claim universal or robust defense effectiveness from n=9 descriptive ASR parity (1/9 vs 1/9).

## S5 — Seed / reproducibility

- Seed `43020260921` recorded; `seed_policy`: honor if provider supports (`protocol freeze`).
- OpenRouter/API does not guarantee bit-exact replay → **configuration reproducibility**, not deterministic token replay.

## S6 — D2 / Adaptive

| Item | In repo? | Live primary evidence? | Primary results? |
|------|----------|-------------------------|------------------|
| D2 (AdaptiGuard) | Yes | Yes (`173736` run) | Yes (paired descriptive) |
| Adaptive studies | Code/docs only | **NOT VERIFIED** for primary | **Excluded** (freeze) |
| Track A/B packs | **NOT IN REPO** | — | **UNSUPPORTED** (P8 §6) |

## S7 — Provider cache / routing

- No HTTP response cache layer in `agent/llm.py`; `lru_cache` in `model_lock.py` caches **config resolution**, not completions.
- Provider order / `allow_fallbacks` sent via `extra_body` when `provider == "openrouter"`.
- **Gap:** metadata in manifest does not cryptographically prove provider route; trust run configuration + gate lock artifacts.

## Engineering notes

| ID | Finding | Action |
|----|---------|--------|
| E1 | PR #2 + #4 **MERGED** to `main` | None |
| E2 | Untracked `test-p42-*` dry runs | **IGNORE** (do not commit) |
| E3 | Root `README.md` described v0 only | **README** updated (research pointer) |
| E4 | Tags `aib-p4.1-frozen-v1.0`, `aib-p4.2-frozen-v1.0`; no post-release tag | Optional human tag on `main` |

## Claim grep summary (docs)

Overclaim phrases appear mainly as **negation / guardrails** in prompts and P8. No unsupported “proven efficacy” in `AIB_FINAL_RESEARCH_READINESS.md`. Qualify any informal “robust” in diagnostic context (COV-C robustness appendix wording).

## Priority backlog

### P0 (manuscript)

- Keep claims within § evidence matrix.
- Cite `173736` only for primary numbers; disclose `130300` gap.

### P1 (submission)

- README ↔ research docs alignment.
- Optional release tag on merge commit.

### P2 (future work)

- Larger N, multi-model, LLM-utility ablation, adaptive/Track A/B, repeated runs, human IAA — **requires new authorized experiments**.
