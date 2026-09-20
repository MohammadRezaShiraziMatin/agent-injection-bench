# Limitations

Honest bounds for agent-injection-bench v0. These should appear in any paper or public summary.

## Dataset

- Small seed: **20 attack + 20 benign** twins — not InjecAgent/AgentDojo scale
- English only; synthetic campus-admin style content
- Pre-bound retrieval — not open-corpus RAG
- No hidden test split; no inter-annotator protocol for utility needles

## Harness and tools

- Mock `search_docs` and `send_email` only; no real delivery
- Bounded tool loop (default max steps 6) — not a dynamic multi-turn attack environment
- No in-repo defense implementation (D2 external)

## Metrics

- ASR-L0/L1 are trace-based tool misuse checks — not full action semantics (L2 unimplemented)
- Utility is substring heuristic — not task-complete scoring or LLM judge
- False-refusal rate not implemented
- API `error` traces excluded from denominators — not counted as safe

## Reproducibility

- Temperature 0 reduces variance; seed is best-effort only
- Provider model strings may map to changing backends
- No published ASR/utility in git until researchers archive live trace bundles

## Defense claims

- D1 is minimal prompt wording for pilot matrices — not a evaluated strong defense
- ADAPTI-GUARD effectiveness requires external D2 runner + separate evidence — [ADAPTI_GUARD_BRIDGE.md](./ADAPTI_GUARD_BRIDGE.md)

## Scope not covered

Direct injection, tool-output injection, memory/state attacks, multi-turn attack design, adaptive attack generation.
