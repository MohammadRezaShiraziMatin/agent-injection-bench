# AIB P4.2 Dataset Freeze Report

**Freeze ID:** `aib-p4.2-frozen-v1.0`
**Branch at freeze:** `cursor/p4-2-dataset-6db2`
**Mode:** Offline verification only (no live LLM, no AdaptiGuard, no dataset regeneration).

---

## 1. Gate result

**PASS WITH CONDITIONS** — P4.2 episode corpus pinned; documented non-blocking limitations remain (harness coverage, P7 off-branch, 8 human `REVISE` verdicts with completed resolution).

---

## 2. Dataset identity

| Field | Value |
|-------|-------|
| Version | P4.2 v1.0 (freeze tag) |
| Episodes | 200 |
| Attack / benign / pairs | 100 / 100 / 100 |
| Schema | `episode.v2.json` |
| Digest | `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee` |

---

## 3. Human review (P4.2.2)

| Verdict | Count |
|---------|------:|
| ACCEPT | 192 |
| REVISE | 8 (`atk_p42_093`–`100`; `revision_resolution` in audit) |
| REJECT | 0 |
| UNCERTAIN | 0 |
| **Total** | **200** |

All 200 episodes have an audit-trail human decision. Eight attacks retain human verdict **REVISE** after metadata-only resolution (Batch 1); not reinterpreted as ACCEPT.

---

## 4. Executability snapshot (dataset metadata)

| Status | Episodes |
|--------|--------:|
| EXECUTABLE | 68 |
| PARTIALLY_EXECUTABLE | 116 |
| DESIGNED_NOT_EXECUTABLE | 16 |

Interpretation: **harness / adapter limitation**, not invalidation of dataset design (`docs/AIB_P4_2_3_HARNESS_ADAPTER_COVERAGE_REPORT.md`).

---

## 5. Quality checks (freeze run)

| Check | Result |
|-------|--------|
| `scripts/qc_p4_2.py` | PASS |
| `scripts/verify_p6_freeze.py` (P4.1) | PASS |
| `scripts/verify_p4_2_freeze.py` | PASS |
| `pytest` | PASS (full suite) |
| P4.1 / v0 episode trees | Unchanged |

---

## 6. Blocking criteria review

Searched canonical docs for requirements that **block** freeze when harness is partial or P7 absent. **None found** that mandate adapter completion or in-tree P7 before pinning P4.2 bytes.

`docs/AIB_P4_2_DATASET_QUALITY_REPORT.md` near-duplicate item satisfied by P4.2.1.

---

## 7. P7 provenance

```text
git log --all -- docs/AIB_P7_EVALUATION_PROTOCOL.md → commit da262d8 (not on current branch HEAD)
P7 on current branch: NOT VERIFIED
```

Does not block dataset freeze per §4 of freeze spec.

---

## 8. Limitations annex (summary)

- Harness v0 does not consume all P4.2 surfaces (`tool_results`, `conversation`, memory/state, `cross_context`, multi-agent, adaptive).
- D1/D2 not implemented in-tree.
- AdaptiGuard live integration out of scope for this freeze.
- P7 live-evaluation protocol not verified on freeze branch.
- Embedding semantic dedup not performed (`qc_p4_2`: `not_performed`).

---

## 9. Commands (recorded)

```bash
python scripts/qc_p4_2.py
python scripts/verify_p6_freeze.py
python scripts/verify_p4_2_freeze.py
pytest -q
git tag -a aib-p4.2-frozen-v1.0 -m "AIB P4.2 dataset freeze v1.0"
```

**No push / release** in this gate.
