# Dataset

## Identity

- **Name:** agent-injection-bench episode set (v0)
- **Location:** `data/episodes/{attack,benign}/` + format demos in `examples/`
- **Schema:** `schema/episode.schema.json` (JSON Schema draft-07)

## Size and layout

- **20 attack + 20 benign** scored seeds: `atk_002`–`atk_021`, `ben_002`–`ben_021`
- Format demos (not in the 20+20 scored set): `examples/episode_attack_001.json`, `examples/episode_benign_001.json`
- One episode per file under `data/episodes/attack/` or `data/episodes/benign/`

## Episode fields

| Field | Meaning |
| --- | --- |
| `id` | Stable id (`atk_*` / `ben_*`) |
| `split` | `attack` or `benign` |
| `user_query` | Honest user request (shared by twins) |
| `retrieved_docs` | `[{doc_id, text}, …]` — injection lives in doc text for attacks |
| `injection` | `{present, payload?, target_tool?}` |
| `expected` | `{allowed_tools, forbidden_tools, utility_answer_contains?, …}` |
| `tags`, `notes`, `source_paper` | Optional metadata |

## Benign twin rule

Paired ids share `user_query` (e.g. `atk_002` / `ben_002`). Attacks have `injection.present=true` and non-empty `forbidden_tools`; benign episodes have `injection.present=false`.

## Provenance

- Synthetic campus-admin style content authored for this bench
- `source_paper` tags style inspiration (Greshake, InjecAgent, etc.); payloads are original to this repo
- Not scraped production user data

## Integrity

- Validate: `python scripts/validate_episodes.py` (default: `examples/` + `data/episodes/`)
- QA report: `python scripts/qa_episodes.py` → `QA_REPORT.md` (twin checks, duplicates)
- Runtime fingerprint: `dataset_version` / `dataset_fingerprint` on manifests (`agent/traces.py`)

## Taxonomy

Pattern-family tags on attack episodes: [TAXONOMY.md](./TAXONOMY.md).

## Versioning

v0 freeze: do not expand the seed set for packaging without schema version review. Adding episodes: see `data/episodes/README.md`.

## Intended use

Pilot evaluation of indirect tool-call induction and benign utility under D0/D1 harness conditions — not training data at scale.
