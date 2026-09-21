# AIB P4.3 — Evaluation Infrastructure Completion Report

**Date:** 2026-09-21 (UTC)  
**Baseline HEAD (pre-work):** `1e46227`  
**Scope:** Harness / evaluation / model-lock readiness for live benchmark — **no P4.2 mutation**, **no dataset expansion**, **no live LLM calls**, **no push/PR/release**.

---

## 1. Baseline

| Item | Value |
|------|--------|
| Branch | `cursor/p4-2-dataset-6db2` |
| P4.2 digest | `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee` |
| P4.3 digest | `e60969bee257ec3111febf215fb5f7079edb79ed050dae300e549336184ab53d` |
| HR | 8/8 ACCEPT (`artifacts/p4_3_hr_audit_trail.json`) |
| Prior gate | PASS WITH CONDITIONS (`docs/AIB_P4_3_COMPLETION_REPORT.md`) |

Pre-work verification: `git diff -- data/episodes_p4_2/` empty; `verify_p4_3_integrity.py` PASS.

---

## 2. Actions completed

### Phase A — S3/S4 execution evidence

- Added `tools/execution_recorder.py` and extended `tools/mock_send_email.py` with structured execution metadata.
- `agent/execution_evidence.py` classifies **S2 / S3 / S4** from proposals + `execution_trace`.
- **S4 external** only when `external_side_effect_occurred=true`; sandbox email log is **S3-side-effect-only**, not external S4.
- `agent/loop.py`, `agent/traces.py`, `agent/evaluation_result.py` propagate `tool_proposals`, `execution_trace`, `observed_success_level`.
- Deterministic tests: `tests/test_execution_evidence.py` (`S2 ≠ S3 ≠ S4`).

### Phase B — Multi-Agent

- **Episode surface:** `INTER_AGENT_REPLAY` / `EXPLICIT_UNSUPPORTED` unchanged (`agent/surface_adapters.py`).
- **New minimal runtime:** `agent/multi_agent_runtime.py` → **`MULTI_AGENT_EXECUTION_SUPPORTED`** (in-process Agent A → Agent B → controlled `send_email`).
- P4.2 DNE episodes remain DNE for episode replay; live multi-agent claims must use the runtime path, not replay alone.

### Phase C — Adaptive

- `agent/adaptive_runtime.py`:
  - **`STATIC_ADAPTIVE_REPLAY`** from `episode.adaptive_trace`
  - **`LIVE_ADAPTIVE`** bounded deterministic loop (seed + max rounds, no external I/O)
- Modes are explicit in `agent/harness_meta.py`; not interchangeable.

### Phase D — Target/Judge model lock

- Extended `agent/config.py` with OpenRouter role loaders + `describe_openrouter_config()` (no secrets in output).
- Gate file: `config/p4_3_live_eval_gate.v1.json` (models **OPEN**, snapshots null).
- `scripts/verify_model_lock.py` — **G2/G3/G4/G10** require evidence; current env → **`MODEL_LOCK_STATUS = BLOCKED`**.

### Phase E — Live evaluation readiness

- `scripts/live_eval_preflight.py` — dry-run only; checks integrity, digest gate, metrics contract, system prompt hash, model lock.
- **`preflight_ok = false`** while model lock blocked → **no live inference executed**.

### Scientific gate

- `scripts/p4_3_scientific_gate.py` → artifact `artifacts/p4_3_scientific_gate.json`.

---

## 3. Files changed (summary)

| Area | Paths |
|------|--------|
| Execution evidence | `tools/execution_recorder.py`, `tools/mock_send_email.py`, `agent/execution_evidence.py`, `agent/tools.py`, `agent/loop.py`, `agent/traces.py`, `agent/evaluation_result.py` |
| Runtime | `agent/multi_agent_runtime.py`, `agent/adaptive_runtime.py`, `agent/harness_meta.py` |
| Model / gate | `agent/config.py`, `config/p4_3_live_eval_gate.v1.json` |
| Scripts | `scripts/verify_model_lock.py`, `scripts/live_eval_preflight.py`, `scripts/p4_3_scientific_gate.py` |
| Tests | `tests/test_execution_evidence.py`, `tests/test_multi_agent_runtime.py`, `tests/test_adaptive_runtime.py`, `tests/test_p4_3_eval_infra.py`, `tests/test_p4_2_4_adapters.py` |

**Not changed:** `data/episodes_p4_2/`, `data/episodes_p4_3/` episode JSON (digest unchanged).

---

## 4. Status matrix

| Component | Status |
|-----------|--------|
| **S3/S4** | Sandbox **execution trace** supported; **external S4 not claimable** in mock environment |
| **Multi-Agent** | **`MULTI_AGENT_EXECUTION_SUPPORTED`** (minimal runtime); episode replay = **`INTER_AGENT_REPLAY_ONLY`** |
| **Adaptive** | **`STATIC_ADAPTIVE_REPLAY`** + **`LIVE_ADAPTIVE`** (bounded, deterministic); episode JSON static traces unchanged |
| **Model lock** | **`BLOCKED`** (no pinned target/judge snapshots + routing in gate) |
| **Live evaluation** | **`BLOCKED`** (preflight fails; zero live calls) |
| **Metrics** | `config/p4_3_evaluation_metrics.v1.json` (unchanged contract, consumed by preflight) |

---

## 5. Tests & integrity

```text
pytest -q  → 61 passed
python scripts/verify_p4_3_integrity.py  → ok: true
python scripts/verify_model_lock.py      → exit 1, MODEL_LOCK_STATUS=BLOCKED
python scripts/live_eval_preflight.py    → preflight_ok: false
python scripts/p4_3_scientific_gate.py   → FINAL_GATE: PASS WITH CONDITIONS
```

Post-work: `git diff -- data/episodes_p4_2/` **empty**.

---

## 6. Remaining blockers (deterministic)

1. Pin **Target** and **Judge** `exact_model_id` + **immutable_snapshot** evidence in `config/p4_3_live_eval_gate.v1.json`.
2. Set `OPENROUTER_TARGET_MODEL`, `OPENROUTER_JUDGE_MODEL`, explicit `OPENROUTER_PROVIDER_ORDER`, `OPENROUTER_ALLOW_FALLBACKS=false`.
3. Flip `preflight.live_inference_allowed` only after `MODEL_LOCK_STATUS=LOCKED` and human approval.
4. External **S4** requires non-sandbox side-effect instrumentation (out of scope for mock email).
5. Statistical claims on P4.3 S1 limited to **n=4** attack pairs.

---

## 7. Scientific limitations

- Dataset completeness ≠ harness completeness ≠ evaluation completeness ≠ live evidence.
- `mock_send_email` proves **sandbox execution**, not SMTP/network **S4**.
- Multi-agent **episode** cohort ≠ multi-agent **runtime** unless `multi_agent_runtime` is used.
- LIVE_ADAPTIVE here is a **deterministic lab loop**, not unbounded attacker autonomy.
- Synthetic episodes do not imply real-world prevalence.

---

## 8. Final gate

| Field | Value |
|-------|--------|
| `DATASET_STATUS` | **PASS** |
| `HARNESS_STATUS` | **PARTIALLY_CLOSED** (S3 sandbox yes; external S4 no) |
| `EVALUATION_STATUS` | **PARTIALLY_CLOSED** (preflight + metrics; no live runs) |
| `LIVE_EVIDENCE_STATUS` | **BLOCKED** |
| `MODEL_LOCK_STATUS` | **BLOCKED** |
| **`FINAL_GATE`** | **`PASS WITH CONDITIONS`** |

Conditions: model lock + live preflight PASS + explicit approval before any live benchmark.
