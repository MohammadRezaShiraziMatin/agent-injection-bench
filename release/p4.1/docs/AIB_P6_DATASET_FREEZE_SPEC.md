# AIB P6 Dataset Freeze Specification

**Freeze ID:** `aib-p4.1-frozen-v1.0`  
**Dataset version:** `P4.1`  
**Identity:** P4.1 is a **controlled reconstruction**, not recovery of historical P4.

---

## 1. Dataset identity

P4.1 is a **new controlled reconstruction** of a 20-episode candidate set under `data/episodes_v1/`.

Historical P4 artifacts were **not recovered** (`docs/AIB_P4_RECOVERY_REPORT.md`, `docs/AIB_P4_ARTIFACT_ARCHIVE_INSPECTION.md`). P4.1 must not be described as restored, recovered, or reconstructed historical P4.

Scientific authorization for freeze: **P5.5 PASS WITH CONDITIONS** with **FREEZE READINESS: AUTHORIZE** (`docs/AIB_P5_5_FINAL_SCIENTIFIC_CLOSURE_REPORT.md`).

P6 does **not** redesign episodes. It pins bytes, hashes, schema, generator, and seed.

---

## 2. Scope

| Item | Frozen value |
|------|----------------|
| Episodes | **20** |
| Attack | **10** (`atk_p41_01` … `atk_p41_10`) |
| Benign | **10** (`ben_p41_01` … `ben_p41_10`) |
| Pairs | **10** (`p41_01` … `p41_10`) |
| v0 | **Not in this freeze** (`data/episodes/` remains a separate baseline) |

**In-scope frozen payload**

```text
data/episodes_v1/
    attack/atk_p41_01.json … atk_p41_10.json
    benign/ben_p41_01.json … ben_p41_10.json
    MANIFEST.json
```

**Pinned companions (not episode content)**

| Role | Path |
|------|------|
| Schema | `schema/episode.v1.json` |
| Generator | `scripts/gen_p4_1_dataset.py` |
| Seed | `41020260920` |
| QC | `scripts/qc_p4_1.py` |
| v0 validator | `scripts/validate_episodes.py` (v0 isolation only) |
| Freeze verifier | `scripts/verify_p6_freeze.py` |
| Tests | `tests/test_p4_1_dataset.py`, `tests/test_p6_freeze.py` |
| Limitations | `docs/AIB_P6_LIMITATIONS_ANNEX.md` |
| Provenance trail | `docs/AIB_P4_1_*`, `docs/AIB_P5_*`, P4 recovery/archive reports |

---

## 3. Integrity

Algorithm: **SHA-256**.

`data/episodes_v1/MANIFEST.json` records:

| Field | Meaning |
|-------|---------|
| `digest_sha256` | Aggregate over **episode files only**: filename + NUL + file bytes (order = sorted episode paths as written by the generator) |
| `episodes[]` | Per file: `episode_id`, `filename`, `sha256`, `byte_size`, `role`, `pair_id` |
| `schema` | `schema/episode.v1.json` |
| `generator` | `scripts/gen_p4_1_dataset.py` |
| `seed` | `41020260920` |
| `freeze_id` | `aib-p4.1-frozen-v1.0` |

**Pinned aggregate digest (episode bytes):**

```text
717458789217d4fd29c655e40018471fdaf16b061ff5481cfdc48f7812437ac3
```

P6 enhanced `MANIFEST.json` with per-file hashes **without changing episode bytes**. The aggregate digest is therefore unchanged from P5.4.1 / P5.5.

Manifest JSON contains **no** absolute paths, usernames, cwd, or timestamps.

---

## 4. Reproducibility

1. `python scripts/gen_p4_1_dataset.py --out <tmpdir>` must emit **byte-identical** episode JSON vs frozen `data/episodes_v1/{attack,benign}/`.
2. The same command must emit **byte-identical** `MANIFEST.json` vs frozen `data/episodes_v1/MANIFEST.json`.
3. `python scripts/gen_p4_1_dataset.py --manifest-only` rewrites only `MANIFEST.json` from existing episode files (used to enhance hashes without touching episodes).
4. `scripts/qc_p4_1.py` two-run regeneration check must remain `byte_identical_regeneration: true`.
5. `scripts/verify_p6_freeze.py` must exit **0** and report hash/count/schema/pair/regen success.

Regeneration for verification **must use a temporary directory** and **must not overwrite** frozen `data/episodes_v1/` episode files.

---

## 5. Compatibility / v0 isolation

| Dataset | Location | Schema | Count |
|---------|----------|--------|------:|
| v0 baseline | `data/episodes/` + `examples/` | `schema/episode.schema.json` | **42** |
| P4.1 freeze | `data/episodes_v1/` | `schema/episode.v1.json` | **20** |

v0 is **not** part of the P4.1 freeze artifact. `git diff -- data/episodes/` must remain empty through P6.

---

## 6. Scientific limitations (frozen annex)

See `docs/AIB_P6_LIMITATIONS_ANNEX.md`. Required statements:

1. Default harness (`agent/loop.py`) loads only `user_query` + `retrieved_docs`.
2. ACF near-duplicate screening passed; **embedding-based semantic paraphrase detection was not performed**.
3. `provenance.review_status=unreviewed` remains **truthful** (schema-locked); P5.4 adjudication is a report, not episode-level review metadata.
4. Benign taxonomy: `objective=benign_control` except schema-required `memory_poisoning` → `unauthorized_state_change` + `objective_note` on `ben_p41_08`; `family` enum still uses `*_injection` channel names.
5. Historical P4 remains **unrecoverable**.

---

## 7. Immutability

After Git tag `aib-p4.1-frozen-v1.0`:

- Do **not** amend the tagged commit.
- Do **not** rewrite frozen episode files in place.
- Defects after freeze require a **new freeze version**, not mutation of v1.0.

---

## 8. Out of scope (P6)

Live LLM evaluation, external APIs, AdaptiGuard, P7 model scoring, new/deleted episodes, payload rewrites, v0 edits, GitHub push/release (unless separately authorized).
