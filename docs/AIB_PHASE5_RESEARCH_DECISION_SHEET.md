# Phase 5 — Research Decision Sheet (FROZEN)

**Status:** FROZEN — controlled paired **descriptive** P4.2 primary protocol.  
**Config:** `config/p4_2_primary_research_protocol_freeze.v1.json`  
**PRELIVE verifier:** `scripts/verify_p4_2_primary_prelive_gate.py`  
**Live execution:** requires separate approval artifacts; not authorized by this freeze alone.

---

## Decision table (D1–D10)

| ID | Research decision | Frozen value | Source | Status |
|----|-------------------|--------------|--------|--------|
| D1 | H3 FPR tolerance τ | **NOT APPLICABLE** as confirmatory threshold; H3 descriptive | Phase 5 freeze; spec §6 | **RESOLVED** |
| D2 | Primary population | **COV-A only** — 9 attack + 9 matched benign (18 episodes) | Primary design MANIFEST; protocol freeze | **RESOLVED** |
| D3 | Primary endpoint | **ASR** (D0 vs D2 on COV-A attacks) | Phase 5 freeze | **RESOLVED** |
| D4 | Sample size / study type | **Descriptive**; n=9 attack pairs; **not** powered confirmatory | Primary MANIFEST `statistical_interpretation` | **RESOLVED** |
| D5 | Repetition | **repetition_count = 1** (frozen historical run); seed unchanged | Gate generation block | **RESOLVED** |
| D6 | Statistical rule | **Descriptive only**; formal hypothesis testing **deferred** | Spec §6; protocol freeze | **RESOLVED** |
| D7 | H3 Utility/FPR | **Descriptively reported**; no automated H3 PASS/FAIL; no new τ | Metrics + paired FPR contract | **RESOLVED** |
| D8 | Adaptive scope | **Excluded** from P4.2 primary D0/D2; Track A/B separate | Completion reports; protocol freeze | **RESOLVED** |
| D9 | Model scope | GPT-4o-mini target + Llama-3.3-70B judge (locked gate) | `config/p4_3_live_eval_gate.v1.json` | **RESOLVED** |
| D10 | Endpoint hierarchy | Primary: ASR; Secondary: S2/S3/S4/Utility/FPR/transitions; Diagnostic: COV-B/C/extensions | Phase 5 freeze | **RESOLVED** |

---

## Coverage roles

| Class | Role |
|-------|------|
| COV-A | **PRIMARY** (frozen P4.2 primary pool) |
| COV-B | **SECONDARY / extension** (future; not in current 9+9 pool) |
| COV-C | **DIAGNOSTIC** — excluded from primary effectiveness claims |

Spec text updated: general RQ may mention COV-A/B exploration; **frozen P4.2 primary execution** is COV-A only per design manifest.

---

## H3 τ (detector vs FPR)

| Item | Rule |
|------|------|
| H3 numeric τ for confirmatory gate | **Not applicable** |
| `0.25` | Detector **coverage** calibration (`AIB_COVERAGE_AWARE_EVALUATION_PROTOCOL.md`) — not H3 τ |
| `0.60` | AdaptiGuard Track B detector config — not H3 τ |

---

## Historical vs protocol

| Layer | Rule |
|-------|------|
| Historical run `p42-primary-d0-d2-20260921T173736Z-controlled` | **Immutable** observations |
| This freeze | Governs **interpretation** and **future** runs under same descriptive protocol |

Do not rewrite historical result files.

---

## Gate status

After offline verifier PASS:

```text
PHASE 5 = COMPLETE (research decisions frozen)
PRELIVE_GATE = PASS (protocol + integrity; not live authorization)
LIVE EXECUTION = NOT EXECUTED (by policy for this phase)
```
