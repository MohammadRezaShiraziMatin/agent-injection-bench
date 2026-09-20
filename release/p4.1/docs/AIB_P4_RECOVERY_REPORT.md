# P4 Artifact Recovery Report

**Date:** 2026-09-20 (UTC)  
**Mode:** Recovery only — no dataset generation, no git restore/checkout, no live LLM/API use.

---

## Current Workspace

| Field | Value |
|--------|--------|
| `pwd` | `/workspace` |
| Git top-level | `/workspace` |
| **Branch** | `main` |
| **HEAD** | `6bced24ea34b9325d3d983ead6ff967d469d1378` |
| HEAD description | `Add v0 agent-injection-bench scaffold with episodes, harness, and scorers.` |
| Remote `origin` | `https://github.com/mohammadrezashirazimatin/agent-injection-bench` (fetch/push) |
| `git status --short` | `?? docs/AIB_P5_DATASET_QA_REPORT.md` (untracked from prior P5 turn); recovery adds this report |
| Worktrees | Single: `/workspace` @ `6bced24` |
| Stashes | None |
| Reflog | Clone-only history; no local commits beyond `6bced24` |

**Same repo as P4 checkpoint?** **Same GitHub repository**, but **not the same checkout state** as the reported P4 completion workspace:

- P4 checkpoint implies `data/episodes_v1/` (20 files), `pytest` ≈ **146**, v0 hash **`4c1877abe0ad137c`**.
- This VM checkout is **`main` @ `6bced24`** (minimal v0 scaffold), **`pytest` = 14**, no `episodes_v1/`, v0 hash **does not match** checkpoint (see v0 Preservation).

---

## P4 Checkpoint Evidence

Reported prior checkpoint (not found as artifacts in this environment):

| Claim | Notes |
|--------|--------|
| `data/episodes_v1/` | 20 JSON episodes |
| Composition | 10 attack + 10 benign twins |
| Quality | Schema-valid; deterministic regen byte-identical |
| `review_status` | `unreviewed` on episodes |
| Scripts/docs | `scripts/gen_p4_dataset.py`, `scripts/qc_p4.py`, `docs/AIB_P4_DATASET_PLAN.md`, `docs/AIB_P4_DATASET_REPORT.md` |
| Tests | `pytest` = **146 passed** |
| v0 | **42** episodes, validation 0 errors |
| v0 short hash | **`4c1877abe0ad137c`** |

None of the P4 paths or hash string appear in any reachable git object in this clone (see below).

---

## Filesystem Search

Commands: `find` under `/workspace`, `/home/ubuntu`, `/opt/cursor`; `rg` for markers.

| Target | Result |
|--------|--------|
| Directory `episodes_v1` | **Not found** anywhere searched |
| `scripts/gen_p4_dataset.py` | **Not found** |
| `scripts/qc_p4.py` | **Not found** |
| `docs/AIB_P4_DATASET_PLAN.md` | **Not found** |
| `docs/AIB_P4_DATASET_REPORT.md` | **Not found** |
| JSON with `pair_id`, `review_status`, `episodes_v1` | **Not found** (only mention in `docs/AIB_P5_DATASET_QA_REPORT.md`) |
| Alternate clone `agent-injection-bench` under `/home/ubuntu` | **Not found** |
| `/opt/cursor/artifacts` episode JSON | **No P4 episode artifacts** |

**No files were created, copied, or modified** during search (read-only).

---

## Git History Search

Repository: **27 commits** across all fetched refs; **no commit** touches P4 paths.

| Command / check | Result |
|-----------------|--------|
| `git log --all -- data/episodes_v1` | **Empty** |
| `git log --all -- scripts/gen_p4_dataset.py` | **Empty** |
| `git log --all -- scripts/qc_p4.py` | **Empty** |
| `git log --all -- docs/AIB_P4_DATASET_*.md` | **Empty** |
| `git for-each-ref` + `git ls-tree` grep `episodes_v1\|gen_p4\|qc_p4\|AIB_P4` | **No matches on any ref** |
| `git grep episodes_v1 $(git rev-list --all)` | **No matches** |
| `git grep 4c1877abe0ad137c $(git rev-list --all)` | **No matches** |
| `git grep gen_p4_dataset $(git rev-list --all)` | **No matches** |
| Episode IDs in all `data/` history | Only `atk_002`–`atk_021`, `ben_002`–`ben_021` (v0); **no v1/P4 IDs** |
| `git tag` | **No tags** |
| `git reflog --all` | Clone + reset to `6bced24` only |
| `git fsck --full --no-reflogs` | **No dangling blobs/commits** reported for recovery |
| `git stash list` | Empty |

**P4 COMMIT = NOT IDENTIFIED** — no commit in local or fetched remote history contains the P4 artifact tree or reported hash string.

---

## Remote Search

After `git fetch origin --prune`:

| Remote branch | Tip commit | `episodes_v1` / P4 scripts |
|---------------|------------|----------------------------|
| `origin/main` | `6bced24` | **Absent** |
| `origin/cursor/adaptive-d2-docs-hardening-e6e0` | `aa84a77` | **Absent** |
| `origin/cursor/phase-a-pilot-runbook-8983` | `14845cb` / `aa84a77` | **Absent** |
| `origin/publication/phase-c-publication` | `7446bfd` | **Absent** (v0 `data/episodes/` only) |

**Pytest collection (read-only `git archive` + `pytest --collect-only` in temp dirs, no checkout of workspace):**

| Ref | Tests collected |
|-----|-----------------|
| `origin/main` | **14** |
| `origin/cursor/*` | **14** |
| `origin/publication/phase-c-publication` | **48** |

**No remote branch** exposes `data/episodes_v1/` or **146** tests.

**GitHub code search** (`episodes_v1`, `gen_p4_dataset`, `4c1877abe0ad137c` in repo/user): **rate-limited (HTTP 429)** during recovery; local `git grep` across all commits already found **zero** matches, so remote code search is unlikely to change outcome.

**Related repo `MohammadRezaShiraziMatin/adapti-guard`:** API tree search — **no** `episodes_v1` / `gen_p4` paths.

**Open PRs:** Only docs-focused cursor branches; no P4 dataset commits in listed PR metadata.

---

## Alternate Workspace Search

| Location | Finding |
|----------|---------|
| Cloud Agent runs (same repo, user) | 3 agents: P5 (this run), env verify (IDLE), env setup (ERROR). **No** `batch-fetch-details` transcript on disk containing P4 file payloads. |
| `/tmp/cursor/cloud-agent-transcripts` | **No** `episodes_v1` / `AIB_P4` strings |
| User GitHub repos (list API) | `agent-injection-bench`, `adapti-guard`, archived `LLM-Security-Lab` — **no second bench clone** with v1 data in this environment |

**Conclusion:** P4 artifacts are **not** present on this VM beyond the checkpoint *claims* in chat/P5 report text.

---

## Candidate Artifact Location

**None identified.**

There is no filesystem path, git commit, remote branch, stash, dangling object, or cloud-agent artifact bundle containing the original 20 `data/episodes_v1/*.json` files or P4 generator/QC scripts.

**Most likely explanation (evidence-based, not speculation of commit SHA):** P4 completion was recorded in a **different local workspace** (e.g. user Desktop / unpushed agent session) that **never entered** `origin` or this Cloud Agent build snapshot (`bld-20260920-*` → `main` @ `6bced24`).

---

## Integrity Verification

**Not performed on 20 P4 JSON files** — originals **not found**.

Checkpoint integrity claims (byte-identical regen, schema-valid, `review_status=unreviewed`) **cannot be verified** here.

**No candidate JSON** met the bar for `FOUND_CANDIDATE_ARTIFACTS_NEEDS_VERIFICATION`.

---

## v0 Preservation

| Check | Result |
|--------|--------|
| `git diff -- data/episodes/` | **Empty** (0 bytes) — **v0 episode files untouched** in this recovery run |
| `python scripts/validate_episodes.py` | `ok: true`, `n: 42`, `errors: 0` |
| Checkpoint hash `4c1877abe0ad137c` | **Not present** in repo history; **not reproduced** on this checkout (prior P5 report: `d8115e4355698339` for 40-file `dataset_version`-style digest on `data/episodes/`) |
| Schemas / `data/episodes/` modified in recovery | **No** |

---

## Recovery Decision

**P4_ARTIFACTS_NOT_FOUND**

| Outcome | Value |
|---------|--------|
| 20 original P4 JSON files recovered | **No** |
| Files modified during recovery | **1** — this report only (`docs/AIB_P4_RECOVERY_REPORT.md`) |
| v0 touched | **No** |
| P4 commit identified | **P4 COMMIT = NOT IDENTIFIED** |
| P5 restarted | **No** (per instructions) |

**Recommended next step (human):** Locate P4 on the machine/session where generation ran — unpushed git branch, uncommitted working tree, agent run export, or backup — and push or copy `data/episodes_v1/` + P4 scripts/reports into the repo **without** regenerating episodes in this recovery run.
