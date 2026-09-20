# Paper claims checklist

Canonical repository evidence map: [../docs/CLAIMS.md](../docs/CLAIMS.md).

Before submitting or posting preprint numbers, verify:

- [ ] Every ASR/utility percentage cites scorer JSON with **N**, skipped counts, model, date, `git_head`
- [ ] No dry-run or `execution_status=error` traces in denominators
- [ ] D1 described as minimal prompt condition, not production defense
- [ ] D2 / ADAPTI-GUARD results sourced from external paired runs, not blended with unrelated Track A/B tables
- [ ] Limitations section includes small N, mock tools, substring utility, pre-bound retrieval
- [ ] Twin design and taxonomy described; no overclaim of InjecAgent/AgentDojo parity

Unsupported until evidence exists: leaderboard rankings, adaptive defense wins, L2 delivery success, deterministic seed guarantees.
