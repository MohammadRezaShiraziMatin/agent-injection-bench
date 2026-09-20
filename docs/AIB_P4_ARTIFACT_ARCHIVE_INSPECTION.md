# AIB P4 Artifact Archive Inspection

**Date:** 2026-09-20 (UTC)  
**Task:** Inspect `adapti-guard-HISTORICAL-PACKAGES.tar.gz` for original AIB P4 artifacts (read-only; no restore, no P5, no dataset generation).

---

## Verified facts

| Item | Result |
|------|--------|
| Expected archive path | `/opt/cursor/artifacts/adapti-guard-HISTORICAL-PACKAGES.tar.gz` |
| Archive present at expected path | **No** — path does not exist |
| `/opt/cursor/artifacts/` contents | **Empty directory** (no files) |
| System-wide search (`find /` for `*HISTORICAL-PACKAGES*`, `adapti-guard*.tar.gz`) | **No matches** |
| Expected SHA256 | `69db0131dba660bd270a5bc8116b2ca3f5f45215c0c62234b065cb0797dc086a` |
| SHA256 computed on expected file | **Not performed** — no file to hash |
| Archive listed (`tar -tzf`) | **Not performed** — no archive |
| Extraction to `/tmp/p4_artifact_inspection/` | **Not performed** |
| Files copied into `data/episodes_v1/` | **No** |
| Live LLM / API evaluation | **None** |
| New P4 dataset generated | **No** |
| P5 started | **No** |

### Current repository (unchanged)

| Check | Value |
|--------|--------|
| `HEAD` | `6bced24ea34b9325d3d983ead6ff967d469d1378` |
| Branch | `main` |
| `git diff -- data/episodes/` | **Empty** (0 bytes) |
| `python scripts/validate_episodes.py` | `ok: true`, `n: 42`, `errors: 0` |

---

## Historical artifacts found

**None.** The named historical package tarball was not available on this environment, so no P4 episode JSON, generator, QC script, plan/report, coverage matrix, or `schema/episode.v1.json` could be read from the archive.

---

## Artifacts merely related to P4

**None identified** in the absence of the archive. Prior recovery work (`docs/AIB_P4_RECOVERY_REPORT.md`) already established that reachable git history and remotes for `agent-injection-bench` do not contain `data/episodes_v1/`; that conclusion is unchanged by this step because the archive could not be opened.

---

## Unresolved provenance

- Whether `adapti-guard-HISTORICAL-PACKAGES.tar.gz` exists on the user’s machine, in Cursor artifact upload, or another storage tier is **unknown** on this VM.
- Whether the expected SHA256 would validate if the file were present is **unverified** here (file missing, not hash-mismatched).
- Original P4 commit / git snapshot inside the archive is **unresolved** (archive not inspected).

---

## Archive search detail (inspection commands)

```text
ls -la /opt/cursor/artifacts/adapti-guard-HISTORICAL-PACKAGES.tar.gz
  → No such file or directory

sha256sum /opt/cursor/artifacts/adapti-guard-HISTORICAL-PACKAGES.tar.gz
  → No such file or directory

find / -name '*HISTORICAL-PACKAGES*' -o -name 'adapti-guard*.tar.gz'
  → (no results)
```

No `tar -tzf` / `tar -xzf` was run because there was no verified archive blob to inspect.

---

## P4 dataset inspection (if found)

**N/A** — no extraction directory; no episode IDs, pair IDs, families, `review_status`, manifests, or internal paths to report.

---

## Final decision

**`NO_P4_ARTIFACTS_IN_ARCHIVE`**

*(Archive file not present on this host; SHA256 step could not run. This is not `ARTIFACT_HASH_MISMATCH`, which applies when a file exists but its digest differs from the expected value.)*

---

## Files created by this inspection

- `docs/AIB_P4_ARTIFACT_ARCHIVE_INSPECTION.md` (this report only)

No modifications to `data/episodes/`, schema, tests, or AdaptiGuard.
