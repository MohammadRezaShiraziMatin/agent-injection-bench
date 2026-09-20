# agent-injection-bench

v0 research artifact for **indirect prompt injection** against tool-using agents: a contaminated **retrieved document** may try to induce forbidden tool misuse (typically mock `send_email`).

**Attack data + harness + offline scorers** — not a defense implementation. Complements **ADAPTI-GUARD** (external D2); see [docs/ADAPTI_GUARD_BRIDGE.md](docs/ADAPTI_GUARD_BRIDGE.md).

**No published ASR or utility rates** in this repository until live, scorable traces exist.

## Quick start (offline)

```bash
python -m pip install -e ".[dev]"
python scripts/validate_episodes.py
python -m pytest
```

Full orientation: **[docs/START_HERE.md](docs/START_HERE.md)**.

## What is in the box

| Component | Location |
| --- | --- |
| 20 attack + 20 benign twin episodes | `data/episodes/` |
| Episode schema | `schema/episode.schema.json` |
| Agent harness (mock tools) | `agent/`, `scripts/run_agent.py` |
| Traces / manifests (generated, gitignored) | `results/traces/`, `results/manifests/` |
| Scoring | `scripts/score_asr.py`, `scripts/score_utility.py` |

## Documentation

| Doc | Topic |
| --- | --- |
| [STATUS.md](STATUS.md) | Current state |
| [CHANGELOG.md](CHANGELOG.md) | History |
| [docs/](docs/) | Threat model, benchmark, dataset, evaluation, claims |
| [paper/](paper/) | Draft outline and paper claims checklist |

## Live evaluation

Requires API key and [docs/EXPERIMENT_PROTOCOL.md](docs/EXPERIMENT_PROTOCOL.md). Do not treat dry-run or quota errors as benchmark results.

## License

MIT — see [LICENSE](LICENSE).
