# AIB P7.4 — Target/Judge Model Lock (OpenRouter, P4.3)

**Date:** 2026-09-21 (UTC)  
**Baseline HEAD:** `b803cc2`  
**Branch:** `cursor/p4-2-dataset-6db2`  
**Live LLM inference:** **NOT RUN**  
**P7 status:** `DESCRIPTIVE_METRICS_RECONCILED` (tracked primary run `…173736Z…`; see P8 submission index).

---

## 1. Baseline

| Item | Value |
|------|--------|
| P4.2 digest | `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee` |
| P4.3 digest | `e60969bee257ec3111febf215fb5f7079edb79ed050dae300e549336184ab53d` |
| Prior state | `MODEL_LOCK=BLOCKED`, empty gate models |

---

## 2. Candidate models considered (catalog evidence)

Public catalog: `GET https://openrouter.ai/api/v1/models` (no API key).  
Artifact: `artifacts/openrouter_model_lock_evidence.json`  
Re-verify: `python scripts/verify_openrouter_catalog_evidence.py`

| Role | exact_model_id | Rationale |
|------|----------------|-----------|
| **Target** | `openai/gpt-4o-mini-2024-07-18` | Dated OpenAI slug; `tools` in `supported_parameters`; required for harness tool loop |
| **Judge** | `meta-llama/llama-3.3-70b-instruct` | Distinct vendor/family; stable slug; `hugging_face_id` recorded |

**Not selected:** `~…-latest` aliases, undated floating slugs, missing catalog rows.

**Alternatives reviewed:** `openai/gpt-4o-mini` (undated sibling), various `google/gemini-*-latest` aliases — rejected for float risk.

---

## 3. Selected Target

| Field | Value |
|-------|--------|
| provider | `openrouter` |
| exact_model_id | `openai/gpt-4o-mini-2024-07-18` |
| endpoint_type | `openrouter_chat_completions` |
| immutable_snapshot | catalog entry SHA256 `9104c1913fcc90fe6d34fed6c04ba453b4dc389b4b5426589ce3aafc9665e5e6` |
| upstream_weight_revision | **UNVERIFIED** |
| routing_policy | `provider_order: [OpenAI]`, `allow_fallbacks: false` |

---

## 4. Selected Judge

| Field | Value |
|-------|--------|
| provider | `openrouter` |
| exact_model_id | `meta-llama/llama-3.3-70b-instruct` |
| endpoint_type | `openrouter_chat_completions` |
| immutable_snapshot | catalog entry SHA256 `af876b7ca63198cedb9873cf2ea87057388189e001de86adfd7a81c29f122f25` |
| hugging_face_id | `meta-llama/Llama-3.3-70B-Instruct` |
| upstream_weight_revision | **UNVERIFIED** |
| routing_policy | `provider_order: [Groq]`, `allow_fallbacks: false` |

**Target ≠ Judge:** verified (`openai/…` vs `meta-llama/…`).

---

## 5. Snapshot / revision evidence

| Layer | Status |
|-------|--------|
| OpenRouter catalog row fingerprint | **LOCKED** (SHA256 per model in gate + evidence file) |
| Catalog re-fetch match | `verify_openrouter_catalog_evidence.py` |
| Provider weight / revision digest | **UNVERIFIED** — not attested by OpenRouter catalog alone |

Limitation (non-negotiable): catalog fingerprint ≠ proof of fixed upstream weights; documented in gate `immutable_snapshot.weight_revision_provable: false`.

---

## 6. OpenRouter routing & fallback

| Control | Implementation |
|---------|----------------|
| `allow_fallbacks` | `OPENROUTER_ALLOW_FALLBACKS=false` + gate `routing_policy.allow_fallbacks: false` |
| Provider order | Per-role env `OPENROUTER_TARGET_PROVIDER_ORDER`, `OPENROUTER_JUDGE_PROVIDER_ORDER` or gate defaults |
| Harness wire-up | `agent/llm.py` sends OpenRouter `extra_body.provider` when `config.provider==openrouter` |
| Secrets | Env only; never committed |

---

## 7. Gate results (with env aligned to gate)

Requires: `OPENROUTER_*` models match gate, API key present, `OPENROUTER_ALLOW_FALLBACKS=false`.

| Gate | Meaning | Expected when env aligned |
|------|---------|---------------------------|
| G2 | Target identity | PASS |
| G3 | Judge identity | PASS |
| G4 | Catalog snapshot + routing + no fallbacks | PASS |
| G10 | Live-eval readiness (env + key + above) | PASS |

`MODEL_LOCK_STATUS`: **LOCKED** when all pass (`scripts/verify_model_lock.py`).

`preflight_ok`: **true** with same env (`scripts/live_eval_preflight.py --dry-run`).

`preflight.live_inference_allowed`: **false** until explicit human approval flag flip.

---

## 8. Preflight (dry-run)

Checks: dataset digests, metrics contract, model lock, system prompt hash, config hash — **no chat API calls**.

---

## 9. Tests & integrity

| Check | Result |
|-------|--------|
| `pytest -q` | 63 passed |
| `verify_p4_3_integrity.py` | PASS |
| `verify_openrouter_catalog_evidence.py` | PASS (at lock time) |
| P4.2 / P4.3 dataset git diff | empty |

---

## 10. Remaining blockers

1. **Upstream weight revision** remains UNVERIFIED (intrinsic OpenRouter limitation).
2. **Provider order** (`Groq` for Llama) should be re-validated if OpenRouter provider availability changes (re-run catalog verify).
3. **Live inference** still forbidden until `live_inference_allowed` + human approval.
4. P4.3 S1 sample size n=4 — no broad statistical claims.

---

## 11. Explicit statement

**No live LLM inference was executed in this pass.**  
No API keys appear in git, JSON artifacts, or this document.
