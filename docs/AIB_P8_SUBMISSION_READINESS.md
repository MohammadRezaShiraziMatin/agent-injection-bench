# P8 — Submission evidence index & gap closure (documentation only)

**Status:** Gap-closure packaging for manuscript/submission alignment.  
**SUBMISSION_READINESS:** `SUFFICIENT_FOR_CURRENT_CLAIMS` (descriptive, COV-A n=9; see §9 claim safety).  
**Does not:** change datasets, frozen contracts, historical results, or re-run experiments.

---

## 1. Repository evidence map (verified on branch `cursor/p4-2-dataset-6db2`)

| Evidence | Run / artifact ID | In git? | Role |
|----------|-------------------|---------|------|
| Frozen P4.2 primary protocol | `config/p4_2_primary_research_protocol_freeze.v1.json` | Yes | P5 decisions D1–D10 |
| Decision sheet | `docs/AIB_PHASE5_RESEARCH_DECISION_SHEET.md` | Yes | Interpretation rules |
| Primary design manifest | `artifacts/p4_2_primary_d0_d2_experiment/MANIFEST.json` | Yes | COV-A 9+9 pool |
| **Immutable historical paired live** | `p42-primary-d0-d2-20260921T173736Z-controlled` | Yes (`results/p4_2_paired/…`) | Freeze `historical_run_immutable` |
| P6 re-execution (post key fix) | `p42-primary-d0-d2-20260922T130300Z-controlled` | **No** | See §2 |
| Invalid judge-failure run | `p42-primary-d0-d2-20260922T122759Z-controlled` | **No** | Exclude from claims |
| GitHub Research CI | PR #4 → `.github/workflows/research-ci.yml` | On `cursor/github-research-ci-6db2` vs `main` | Offline integrity |
| Manuscript source | — | **No** | External to repo |
| AdaptiGuard Track A/B packs (prompt SHAs) | — | **NOT EVIDENCED** in tree | Do not cite without artifact |

---

## 2. G1-P6-ARTIFACT — recovery result

**Discovery (read-only):** No path, commit, branch, stash, or GitHub Actions artifact contains  
`results/p4_2_paired/p42-primary-d0-d2-20260922T130300Z-controlled/`.

**Rule:** No reconstruction, copy-rename, or summary-as-raw substitution.

**Submission path 1 (current repo):** Use **tracked** run  
`p42-primary-d0-d2-20260921T173736Z-controlled` as the reproducible primary paired live evidence.  
Descriptive metrics (scorer, `descriptive_only: true`):

- ASR D0/D2: 1/9 each (11.11%)
- Utility D0/D2: 9/9 (100%)
- FPR D0/D2: 0/9 (0%)
- Judge failures: 0 on 36 records (verify with `RESULTS.json` + `score_p4_3_paired_metrics.py`)

**Submission path 2:** If operators retain an offline copy of `…130300Z-controlled`, publish it as a **separate immutable archive** (checksum + manifest) without editing bytes. Do not fabricate in git.

**Status:** `G1-P6-ARTIFACT = UNRESOLVED` for run ID `130300` in repository; **mitigated** for submission via path 1 if manuscript cites `173736` and limitations.

---

## 3. G1-N9 — limitations (no sample change)

Frozen design: 9 attack + 9 matched benign, COV-A, `repetition_count=1`, descriptive only.

**Manuscript must:**

- Avoid population-level efficacy, superiority, generalization, significance.
- Report sample-level observations only.
- State external validity limited to this primary pool.

**Future work:** See `docs/AIB_P8_FUTURE_EXPERIMENT_PROTOCOL_DRAFT.md` (not executed).

---

## 4. G1-WEIGHT

`upstream_weight_revision = UNVERIFIED` (protocol freeze + model lock).  
No weight-sensitive defense claims until reproducible revision evidence exists.

---

## 5. G1-JUDGE

Judge: `meta-llama/llama-3.3-70b-instruct` (operational evaluator per gate).  
No human inter-rater or IAA in repository — document as limitation; do not treat judge as ground truth.

---

## 6. G1-TRACK

Track A/B outcomes referenced in project prompts are **NOT EVIDENCED** in this repository (no pack SHA files, no result bundles).  
Exclude from primary P4.2 narrative or add external supplementary with provenance.

---

## 7. G2-MAIN / G2-CI-POLICY

- Research release merged to `main` (PR #2); CI workflow on `main` (PR #4 merge).
- Historical development branch: `cursor/p4-2-dataset-6db2` (same content at release merge).
- **Required check names (from GitHub):** `Tests`, `Research Integrity`, `Security / Workflow Validation` (workflow: Research CI).
- Branch protection: **ADMIN_ACTION_REQUIRED** (API not writable from agent). Administrator should require the three jobs above on `main` after merge.

---

## 8. G2-MANUSCRIPT

No manuscript in repo. Claim audit must run when source is available.  
Use table template in §9.

---

## 9. Claim safety (P4.2 primary, descriptive)

| Claim | Evidence | Manuscript status |
|-------|----------|-------------------|
| Paired D0 vs D2 on COV-A primary pool | Tracked run + freeze + scorer | SUPPORTED (descriptive, n=9) |
| ASR reduction with D2 | Same | **OVERSTATED** if claimed — observed ΔASR = 0 |
| Utility/FPR unchanged in benign sample | Same | SUPPORTED (descriptive) |
| Defense efficacy / superiority | — | **UNSUPPORTED** at this n |
| Statistical significance | P5 deferred | **UNSUPPORTED** |
| Track A/B / adaptive primary | — | **NOT EVIDENCED** in repo |
| Q1 acceptance | — | **UNSUPPORTED** |

---

## 10. G3-LITERATURE

Deferred to manuscript authoring; cite primary sources per venue. No automated Q1 guarantee.

---

## 11. Reproducibility checklist (reviewer)

1. Checkout `cursor/p4-2-dataset-6db2` (or release tag once created).
2. `pip install -e ".[dev]"`; optional AdaptiGuard pin per `config/adaptiguard_version_pin.v1.json`.
3. `pytest -q`; `python scripts/verify_p4_2_freeze.py`; `verify_p4_2_primary_prelive_gate.py`.
4. Score tracked run:  
   `python scripts/score_p4_3_paired_metrics.py results/p4_2_paired/p42-primary-d0-d2-20260921T173736Z-controlled`
5. Do not expect `…130300Z…` in git unless separately archived.
