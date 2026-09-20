# AIB P4.2 Dataset Card

## Dataset summary

**Agent Injection Bench P4.2** — 200 synthetic campus-assistant episodes (100 attack / 100 benign) with paired controls, V2 taxonomy, and explicit executability metadata. Candidate release; not frozen.

## Motivation

Provide broader mechanism and family coverage than frozen P4.1 while keeping evaluation defense-agnostic and reproducible.

## Scope

- Prompt / indirect / multi-turn / RAG / web-snippet / tool-output / memory-state / cross-context attacks
- Multi-agent and adaptive families included as **designed, non-executable** specifications until harness adapters exist
- Campus-themed contexts only; mock `send_email` targets use `*.example.invalid`

## Intended use

- Benchmark design and adapter development
- Offline QC, leakage, and deduplication methodology regression
- Stratified splits for future live evaluation (after P7 model lock and harness extensions)

## Out-of-scope use

- Claiming real-world attack success rates without live evaluation
- Training on `test` partition labels for tuning generators
- Inferring AdaptiGuard or D2 effectiveness from dataset files alone

## Data composition

| Split role (`split`) | Count |
|----------------------|------:|
| attack | 100 |
| benign | 100 |

| Partition (`dataset_partition`) | Attack pairs |
|---------------------------------|-------------:|
| development | 60 |
| validation | 20 |
| test | 20 |

## Taxonomy

See `docs/AIB_P4_2_TAXONOMY_V2.md`.

## Collection / authoring

Programmatic generation (`scripts/gen_p4_2_dataset.py`, `scripts/p4_2_episode_bank.py`). **Not human-authored.**

## Generation

- Seed: `42020260920`
- No network / LLM / API calls
- Manifest: `data/episodes_p4_2/MANIFEST.json`

## Annotation

Synthetic labels with `review_status=unreviewed`. Success criteria S0–S2 documented per episode.

## Quality control

`scripts/qc_p4_2.py`, `scripts/semantic_dedup_p4_2.py`, `tests/test_p4_2_dataset.py`.

## Known limitations

Partial harness execution; 114 n-gram near-duplicate flags for human review; 200 episodes (minimum tier).

## Ethical / safety considerations

Synthetic scenarios; no real PII; exfiltration targets are example.invalid addresses.

## Reproducibility

Byte-identical regeneration required and tested.

## Versioning

- P4.1: frozen pilot (`aib-p4.1-frozen-v1.0`)
- P4.2: candidate (no freeze tag)

## Citation information

Repository: `agent-injection-bench`. Cite dataset version `P4.2`, manifest digest, and generator version `gen_p4_2_dataset.py@1.0.0`.
