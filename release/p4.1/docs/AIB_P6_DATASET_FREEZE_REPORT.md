# AIB P6 Dataset Freeze Report

**Freeze ID:** `aib-p4.1-frozen-v1.0`  
**Date of freeze operations:** 2026-09-20 (UTC)  
**Mode:** Offline; no LLM/API; no episode content edits; v0 untouched  
**Prior gate:** P5.5 **PASS WITH CONDITIONS** — **FREEZE READINESS: AUTHORIZE**

---

## 1. Executive Summary

P6 freezes the audited P4.1 reconstruction as a hash-addressed, regenerable artifact.

| Item | Result |
|------|--------|
| Episode bytes changed in P6 | **0** |
| Aggregate digest | `717458789217d4fd29c655e40018471fdaf16b061ff5481cfdc48f7812437ac3` (unchanged from P5.4.1/P5.5) |
| Per-file SHA-256 | Added to `data/episodes_v1/MANIFEST.json` |
| Release package | `release/p4.1/` |
| Git tag | `aib-p4.1-frozen-v1.0` (annotated; **not pushed**) |
| **P6 gate** | **`P6 PASS`** |

P4.1 remains a **controlled reconstruction**, not historical P4 recovery. **P7 was not started.**

---

## 2. Freeze Scope

| In scope | Out of scope |
|----------|----------------|
| Pin 20 P4.1 JSON episodes + MANIFEST | New/deleted episodes |
| SHA-256 records | Payload or taxonomy semantic edits |
| Freeze spec, annex, verifier, tests | Live LLM / AdaptiGuard / P7 |
| Deterministic `release/p4.1/` | v0 `data/episodes/` |
| Annotated local Git tag | GitHub push/release |

---

## 3. Dataset Inventory

| Item | Count |
|------|------:|
| P4.1 episodes | **20** |
| Attack | **10** |
| Benign | **10** |
| Pairs (`p41_01`–`p41_10`) | **10** |
| v0 (isolated) | **42** |

IDs: `atk_p41_01`–`atk_p41_10`, `ben_p41_01`–`ben_p41_10`.

---

## 4. Manifest / Hashes

`data/episodes_v1/MANIFEST.json`:

| Field | Value |
|-------|--------|
| `dataset_version` | `P4.1` |
| `freeze_id` | `aib-p4.1-frozen-v1.0` |
| `identity` | P4.1 controlled reconstruction (not historical P4 recovery) |
| `schema` | `schema/episode.v1.json` |
| `generator` | `scripts/gen_p4_1_dataset.py` |
| `seed` | `41020260920` |
| `digest_sha256` | `717458789217d4fd29c655e40018471fdaf16b061ff5481cfdc48f7812437ac3` |
| `episode_count` / `attack_count` / `benign_count` / `pair_count` | 20 / 10 / 10 / 10 |

### Per-episode SHA-256

| episode_id | filename | role | pair_id | byte_size | sha256 |
|------------|----------|------|---------|----------:|--------|
| atk_p41_01 | attack/atk_p41_01.json | attack | p41_01 | 1867 | `5648fbbceab531948bbcf521f0cda3ff2040f1c78d6f1695f4470a9d21572d08` |
| atk_p41_02 | attack/atk_p41_02.json | attack | p41_02 | 1861 | `8a0fa31a69d2be0c95520aebe2593891f637ba28d9e5417f3e85ce65f59bc8e3` |
| atk_p41_03 | attack/atk_p41_03.json | attack | p41_03 | 1964 | `229c1250b6c212a08fb7aa70085f6a5a69a4cdb25ad3a35b63ef231e3e90bd05` |
| atk_p41_04 | attack/atk_p41_04.json | attack | p41_04 | 1963 | `93aa34a35456686a1ecae8c72c55f2402f91dd3a99ebca14705ed00734491395` |
| atk_p41_05 | attack/atk_p41_05.json | attack | p41_05 | 2204 | `0d0e931920369d7915cecfe9b983a879ca0a2bcbc0038222eaeb387d53c32cb9` |
| atk_p41_06 | attack/atk_p41_06.json | attack | p41_06 | 1900 | `c6622af4108ee27e01d84edcf0db53f332304ef9f5121bd573d75d092a6f0cfe` |
| atk_p41_07 | attack/atk_p41_07.json | attack | p41_07 | 1908 | `a3acc32e854e26af0d90f4d08cfcab3136a8e3ff4196ef9f031fdb72b32f5be6` |
| atk_p41_08 | attack/atk_p41_08.json | attack | p41_08 | 2136 | `95ac9db088a5c934d1d09df7748803d8eea106485a2ee6ade75246129740a429` |
| atk_p41_09 | attack/atk_p41_09.json | attack | p41_09 | 1869 | `65e8b4598fee8d5cd00865957faf534cea9f3626839439bfa9f1d7a401bdf3ca` |
| atk_p41_10 | attack/atk_p41_10.json | attack | p41_10 | 1925 | `05db87d927a942376f615e4d28b8a854a1c1e2de8e2b671540e8539207c87095` |
| ben_p41_01 | benign/ben_p41_01.json | benign | p41_01 | 1811 | `c1980d5a1bd40ed9e7da56d4bc8229ee26c0d1758806157180e58b692543ace5` |
| ben_p41_02 | benign/ben_p41_02.json | benign | p41_02 | 1800 | `df691464d7c17e27bee63bd5eb8f1225c4dd85fbcd91855bc99bdb202f8b6fcd` |
| ben_p41_03 | benign/ben_p41_03.json | benign | p41_03 | 1892 | `8fe076c6e27ea7a36fb3beec938ae314b180ce1e3c6bbd3f6d775d16252ba487` |
| ben_p41_04 | benign/ben_p41_04.json | benign | p41_04 | 1974 | `8751312800683283be9f7cb26d7385a47d685bc9f9bb8fb3e5110e572402f786` |
| ben_p41_05 | benign/ben_p41_05.json | benign | p41_05 | 2112 | `b4ca3cf3fd1aa35f8e6a3f7edd8385df620af51409ce0fad06d5f2f87365f00b` |
| ben_p41_06 | benign/ben_p41_06.json | benign | p41_06 | 1906 | `90b5ef8fa628402acea3aa7b985027e425d4471d471b8e07ee6d2eaffae1fa3d` |
| ben_p41_07 | benign/ben_p41_07.json | benign | p41_07 | 1801 | `7773bef39027afe75e5f07d7ddb7e7182e8fe2387c9d4f279be587b561b7d543` |
| ben_p41_08 | benign/ben_p41_08.json | benign | p41_08 | 1910 | `292b38999a9debb93c0b7d512361dc6ecd5cde6980e6fe6d2d86e770644289b5` |
| ben_p41_09 | benign/ben_p41_09.json | benign | p41_09 | 1835 | `7938a6c9d704881737304f78f4aedf20a20f6a2258a2505256d09e668a02d9d0` |
| ben_p41_10 | benign/ben_p41_10.json | benign | p41_10 | 1905 | `fe1916365fd83f2da45ccf892c0de7269a17e06c3b887d1d02ca95fee6d20e5e` |

---

## 5. Schema

| Dataset | Schema path | Status |
|---------|-------------|--------|
| P4.1 | `schema/episode.v1.json` (`schema_version` 1.0) | Frozen companion |
| v0 | `schema/episode.schema.json` | Unchanged; not part of P4.1 freeze |

---

## 6. Generator + Seed

| Item | Value |
|------|--------|
| Generator | `scripts/gen_p4_1_dataset.py` |
| Seed | `41020260920` |
| Manifest-only mode | `--manifest-only` (hashes only; does not rewrite episodes) |

---

## 7. Reproducibility

Regeneration is verified in a **temporary directory**; frozen episode files are not overwritten.

Expected: `byte_identical_regeneration = true` for episodes **and** `MANIFEST.json`.

---

## 8. Validation

Recorded at freeze time (see §13 for commands):

| Check | Result |
|-------|--------|
| `scripts/validate_episodes.py` (v0) | **42/42**, 0 errors |
| P4.1 schema (v1) | **PASS** (20/20) |
| `scripts/qc_p4_1.py` | **PASS**, `byte_identical_regeneration: true` |
| `pytest -q` | **PASS** |
| `scripts/verify_p6_freeze.py` | **PASS** |

---

## 9. v0 Isolation

| Check | Result |
|-------|--------|
| v0 count | **42** |
| `git diff -- data/episodes/` | **empty** |
| v0 included in `release/p4.1/` episode payload | **No** (`includes_v0_episodes: false`) |

---

## 10. Provenance

> **P4.1 remains a controlled reconstruction, not recovery of historical P4.**

Episode provenance (unchanged): `reconstruction=P4.1`, `synthetic=true`, `human_authored=false`, `review_status=unreviewed`.

Governance trail: P4.1 plan/report → P5–P5.5 → this freeze.

---

## 11. Limitations Annex

See `docs/AIB_P6_LIMITATIONS_ANNEX.md`:

- **L1** harness coverage (`user_query` + `retrieved_docs` only)
- **L2** embedding paraphrase **not performed**
- **L3** `review_status=unreviewed` truthful
- **L4** benign taxonomy caveat
- **L5** historical P4 unrecoverable

---

## 12. Release Artifact

Path: `release/p4.1/`

```text
release/p4.1/
├── RELEASE_MANIFEST.json
├── data/episodes_v1/
├── docs/
├── schema/episode.v1.json
├── scripts/
└── tests/
```

Built by `scripts/build_p6_release.py` (fixed file list including the builder; SHA-256 per packaged path; no `.git`, caches, credentials, traces, or v0 episode JSON). Package `file_count` is recorded in `release/p4.1/RELEASE_MANIFEST.json`.

---

## 13. Freeze Verification

Commands (repo root, offline):

```text
python scripts/validate_episodes.py
python scripts/qc_p4_1.py
python scripts/verify_p6_freeze.py
pytest -q
python scripts/build_p6_release.py
```

`verify_p6_freeze.py` checks: manifest presence, file existence, SHA-256 match, counts 20/10/10/10, schema, unique IDs, pair structure, temp-dir regeneration.

---

## 14. Final Gate

**`P6 PASS`**

All freeze integrity criteria met: 20/20 episodes, hashes, schema, QC, tests, deterministic regeneration, v0 unchanged, provenance and limitations documented, release package created, annotated tag created, no post-tag episode mutation, **no GitHub push/release**.

---

## 15. Machine-readable summary

```text
P6 GATE: PASS

FROZEN DATASET:
- version: P4.1
- episodes: 20
- attacks: 10
- benign: 10
- pairs: 10
- manifest SHA: 717458789217d4fd29c655e40018471fdaf16b061ff5481cfdc48f7812437ac3
- schema: schema/episode.v1.json
- generator: scripts/gen_p4_1_dataset.py
- seed: 41020260920

VALIDATION:
- v0: 42/42
- P4.1 schema: PASS
- QC: PASS
- pytest: PASS
- reproducibility: PASS
- freeze verification: PASS

INTEGRITY:
- episode hashes: PASS
- v0 diff: EMPTY
- post-tag mutation: NONE

RELEASE:
- package: CREATED
- Git tag: aib-p4.1-frozen-v1.0
- GitHub push: NO
- GitHub release: NO

LIMITATIONS:
- runtime harness coverage: documented
- embedding paraphrase detection: not performed
- review_status: unreviewed/truthful
- benign taxonomy caveat: documented
- historical P4: unrecoverable

P7: NOT STARTED
LIVE LLM: NO
ADAPTIGUARD: NO
```
