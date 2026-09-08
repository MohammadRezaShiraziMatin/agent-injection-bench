# DATA_CARD

## Identity

- **Name:** agent-injection-bench episode set (v0)
- **Location:** `data/episodes/{attack,benign}/` + `examples/` demos
- **Schema:** `schema/episode.schema.json`

## Version / integrity

- Content baseline commit: `7ec8eb7b6f6e9671a9de653670f16fcf01bcf5de`
- Runtime fingerprint helpers: `agent/traces.dataset_version` / `dataset_fingerprint` (when manifests are written)

## Provenance

- Synthetic campus-admin style FAQs authored for this bench
- Some episodes tagged with style inspiration (`source_paper` / tags); payloads are original to this repo
- Not scraped production user data

## Structure

- **20 attack + 20 benign** twins (same `user_query`; dirty vs clean docs)
- Format demos: `atk_001` / `ben_001` in `examples/` (not the scored 20+20)
- Fields: `id`, `split`, `user_query`, `retrieved_docs`, `injection`, `expected`, optional `tags` / `notes` / `source_paper`

## Categories

- See `TAXONOMY.md` (injection pattern tags)

## Intended use

- Pilot evaluation of indirect tool-call induction and benign utility under D0/D1 harness conditions

## Out of scope

- Training general jailbreak detectors on this tiny set alone
- Claiming ecological validity for all enterprise agents
- Adaptive/D2 evaluation data (none in-repo)

## Limitations / contamination

- Small N; English only; pre-bound docs
- Models trained on public web may have seen similar “ignore previous instructions” patterns — not quantified here
- Substring utility needles can be weak; see scorers

## Versioning

- Freeze growth unless schema version bumps; regenerate only via reviewed scripts
