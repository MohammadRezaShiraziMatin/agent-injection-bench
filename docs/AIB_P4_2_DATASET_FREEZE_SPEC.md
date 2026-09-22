# AIB P4.2 Dataset Freeze Specification

**Freeze ID:** `aib-p4.2-frozen-v1.0`
**Dataset version:** `P4.2`
**Label:** Expanded benchmark candidate (200 episodes), frozen as a **dataset artifact** independent of harness adapter completeness or live evaluation.

---

## 1. Scope

| Item | Frozen value |
|------|----------------|
| Episodes | **200** |
| Attack | **100** (`atk_p42_001` … `atk_p42_100`) |
| Benign | **100** (`ben_p42_001` … `ben_p42_100`) |
| Pairs | **100** (`p42_001` … `p42_100`) |
| Schema | `schema/episode.v2.json` (2.0) |
| Generator | `scripts/gen_p4_2_dataset.py` |
| Seed | `42020260920` |

**Frozen payload (episode bytes):**

```text
data/episodes_p4_2/
    attack/*.json
    benign/*.json
    MANIFEST.json   (metadata; episode aggregate digest below)
```

**Out of scope for this freeze**

- v0 (`data/episodes/`) — separate baseline
- P4.1 (`data/episodes_v1/`) — frozen under `aib-p4.1-frozen-v1.0`
- Live LLM runs, P7 scoring, AdaptiGuard, D1/D2 defense implementations

---

## 2. Integrity

**Pinned aggregate digest (episode JSON files only, sorted by filename):**

```text
4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee
```

Verifier: `scripts/verify_p4_2_freeze.py`, `scripts/qc_p4_2.py`.

---

## 3. Scientific closure prerequisites (met at freeze)

| Gate | Status |
|------|--------|
| P4.2.1 near-duplicate adjudication | Complete (`artifacts/p4_2_1_near_duplicate_adjudication.json`) |
| P4.2.2 human review | **200/200** audit decisions (`artifacts/p4_2_2_hr_audit_trail.json`) |
| P4.2.3 harness coverage audit | Documented (`docs/AIB_P4_2_3_HARNESS_ADAPTER_COVERAGE_REPORT.md`) |
| QC / pairing / leakage / reproducibility | `scripts/qc_p4_2.py` |

---

## 4. Non-blocking limitations (explicit)

These do **not** block dataset freeze:

| Limitation | Evidence |
|------------|----------|
| **116** `PARTIALLY_EXECUTABLE` / **16** `DESIGNED_NOT_EXECUTABLE` | Harness v0 (`agent/loop.py`) consumes `user_query` + `retrieved_docs` only; see P4.2.3 report |
| D1 / D2 | Contract-only in this repository |
| AdaptiGuard | External bridge (`docs/ADAPTI_GUARD_BRIDGE.md`); not integrated |
| P7 protocol files | Not on branch `cursor/p4-2-dataset-6db2` at freeze time (evaluation is a separate phase) |
| **8** human `REVISE` decisions | Batch 1 attacks `atk_p42_093`–`100`; metadata resolution recorded in audit; episode bytes updated before digest pin |

No canonical document requires full harness surface coverage or P7 availability **before** pinning P4.2 episode bytes.

---

## 5. Immutability after tag

After `aib-p4.2-frozen-v1.0`:

- Do not modify frozen episode bytes or aggregate digest without a new versioned freeze.
- Harness adapters and live evaluation may proceed on separate tracks.
