# Intro + Contributions draft (paper paste)

**Note:** Draft only. Align notation and citations with the rest of the paper. No empirical ASR/utility claims from this artifact alone.

---

## Intro paragraph

Large language model agents that retrieve documents and call tools can be steered by **indirect prompt injection**: malicious instructions embedded in untrusted retrieved content rather than in the user’s request. Measuring that failure mode requires fixed tasks, a clear misuse criterion (e.g., calling a restricted tool), and traces that can be scored without conflating API errors with attack success. We release **agent-injection-bench**, a small academic seed and measurement harness (D0 undefended baseline; optional minimal D1 prompt condition for pilot matrices), positioned as a complement to separate defense work (ADAPTI-GUARD / D2 external), not as a large benchmark or a strong-defense evaluation.

## Contributions

- A frozen **20 attack / 20 benign** twin episode seed with injection confined to retrieved documents and a shared honest user query.
- A minimal tool surface (**mock** `search_docs` and `send_email` only) and an undefended Phase-2 LLM tool loop that writes auditable traces.
- Offline ASR and utility **definitions** (stubs) that exclude error and dry-run traces; metrics are for future researcher runs, not reported rates in this release.
- Packaging for honest reuse: schema, validation, runbook, and explicit non-goals (no in-repo defense, no leaderboard claims, no fabricated numbers).
- A clear interface sketch toward later defended runners that reuse the same episode/trace format while keeping scorers unchanged.
