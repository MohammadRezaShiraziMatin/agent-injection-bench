# Draft snippets (intro + related work)

Moved from legacy root drafts. No empirical rates.

## Intro

# Intro + Contributions draft (paper paste)

**Note:** Draft only. Align notation and citations with the rest of the paper. No empirical ASR/utility claims from this artifact alone.

---

## Intro paragraph

Large language model agents that retrieve documents and call tools can be steered by **indirect prompt injection**: malicious instructions embedded in untrusted retrieved content rather than in the userâ€™s request. Measuring that failure mode requires fixed tasks, a clear misuse criterion (e.g., calling a restricted tool), and traces that can be scored without conflating API errors with attack success. We release **agent-injection-bench**, a small academic seed and measurement harness (D0 undefended baseline; optional minimal D1 prompt condition for pilot matrices), positioned as a complement to separate defense work (ADAPTI-GUARD / D2 external), not as a large benchmark or a strong-defense evaluation.

## Contributions

- A frozen **20 attack / 20 benign** twin episode seed with injection confined to retrieved documents and a shared honest user query.
- A minimal tool surface (**mock** `search_docs` and `send_email` only) and an undefended Phase-2 LLM tool loop that writes auditable traces.
- Offline ASR and utility **definitions** (stubs) that exclude error and dry-run traces; metrics are for future researcher runs, not reported rates in this release.
- Packaging for honest reuse: schema, validation, runbook, and explicit non-goals (no in-repo defense, no leaderboard claims, no fabricated numbers).
- A clear interface sketch toward later defended runners that reuse the same episode/trace format while keeping scorers unchanged.


## Related work

# Related Work draft (paper paste)

**Note:** Draft text for a paper. Replace in-text citations with the venueâ€™s bibliography style (ACL/NeurIPS/IEEE, etc.) as needed. This repository publishes **no** ASR or utility rates.

---

Indirect prompt injection (IPI) arises when untrusted content ingested by an LLM-integrated application steers model behavior away from the userâ€™s intent (Greshake et al., 2023, arXiv:2302.12173). Subsequent work both benchmarks IPI and studies defenses (Yi et al., 2023, arXiv:2312.14197). We focus on the **indirect**, retrieval- and tool-mediated setting rather than classical **direct** prompt injection in which the adversary controls the user prompt alone.

Tool-using agents are a particularly relevant target: success may mean inducing unintended tool calls rather than only corrupted text. InjecAgent evaluates IPI against tool-integrated agents at large scale (Zhan et al., 2024, arXiv:2403.02691; on the order of 1054 cases in that work). AgentDojo provides a dynamic environment for evaluating prompt-injection attacks and defenses on LLM agents (Debenedetti et al., 2024, arXiv:2406.13352).

**agent-injection-bench** is a complementary measurement artifact, not a replacement for those suites. It supplies a small fixed seed of **20 attack and 20 benign** twin episodes that share an honest user query while placing injections only in retrieved documents; two mock tools (`search_docs`, `send_email`); an undefended OpenAI-compatible agent loop; and auditable traces for offline scoring. Attack success rate (ASR) and utility metrics are **defined** in the accompanying stubs for researcher-run evaluation after live, non-error traces exist; this draft does not report empirical rates. Runtime defenseâ€”including ADAPTI-GUARDâ€”is intentionally **out of scope** here and belongs to a separate line of work that can later consume the same episode and trace schemas.

### What this artifact is not

- Not a large IPI suite comparable to InjecAgentâ€™s scale.
- Not a dynamic agent environment in the sense of AgentDojo.
- Not a defense implementation or defense evaluation (no ADAPTI-GUARD code or guarded results in this artifact).
- Not a source of published ASR/utility numbers until researchers obtain scorable live traces.

