# ADAPTI-GUARD bridge

This repository is **attack + evaluation only**. It does **not** vend ADAPTI-GUARD. D2 wiring lives in `agent/defense/adaptiguard_bridge.py` and expects an external Python package exposing `guard_messages(episode=..., messages=..., dry_run=...)`.

Intended integration (separate project):

1. Consume the same frozen `episode.schema.json` and episode JSON.
2. Wrap or replace the harness loop with a defense stack (e.g., D0 none → D5 ADAPTI-GUARD).
3. Emit compatible traces under `results/traces/` so `score_asr.py` / `score_utility.py` remain valid.
4. Never fork the schema for defense-specific fields without a versioned bump.

Bridge checklist for the defense repo:

- [ ] Import episodes read-only from this bench (or submodule/copy with pin)
- [ ] Keep tool names `search_docs` / `send_email` stable for scoring
- [ ] Log defense decisions in a side channel; do not break ASR tool-call detection
- [ ] Publish defense rates only from executed paired runs

See also historical ATEA notes: defenses live outside this tree.
