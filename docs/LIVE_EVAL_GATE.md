# Live eval gate (design only)

Human and technical gates before spending API budget on **live LLM** calls in agent-injection-bench. This does **not** authorize a run by itself — explicit human sign-off is required.

**Default: API=0.** Contributors and CI should stay offline unless this gate is satisfied.

Level A evidence already on `main` comes from **completed frozen paired runs** with their own approval artifacts under `config/` — this gate governs **new** live inference (v0 harness pilot, new research batches, or re-runs), not re-reading archived bundles.

---

## 1. Preconditions (offline green)

All must pass with **no** `AIB_LLM_API_KEY`:

```bash
python3 scripts/validate_episodes.py
python3 -m pytest
python3 scripts/run_agent.py --smoke --dry-run
```

Record commit SHA and date in the sign-off record.

---

## 2. Human sign-off (required)

Before any live call:

| Field | Requirement |
|-------|-------------|
| **Approver** | Named human (not the agent) |
| **Purpose** | e.g. “v0 Phase A full batch”, “smoke only (2 eps)”, or named frozen protocol run |
| **Episode scope** | Exact ids, `--split` + `--limit`, or protocol population |
| **Model pin** | `AIB_LLM_MODEL` + provider (must match protocol if research run) |
| **Budget cap** | Max spend or max episodes × estimated tokens |
| **Target ≠ Judge** | UUT model id ≠ automated judge endpoint used for auxiliary labels |
| **Cache policy** | Cache disabled for provider/client (document how) |
| **Trace hygiene** | Plan to `rm -f results/traces/*.json` before v0 live batch if dry-run files exist |

Sign-off may be a ticket, email, or lab log — not committed secrets.

---

## 3. API key handling

- Copy `.env.example` → `.env`; set `AIB_LLM_API_KEY` only after sign-off.
- Never commit `.env` or keys.
- Rotate keys after pilot if policy requires.

Optional: `AIB_LLM_BASE_URL`, `AIB_LLM_MODEL`.

---

## 4. Stop rules (during live run)

Stop immediately and preserve partial traces if:

1. **Budget exceeded** — halt batch; do not silently continue.
2. **Schema / harness error** — fix offline; do not patch forward mid-batch without new sign-off.
3. **Provider outage or rate limit storm** — pause; partial `n` is **partial** ([CLAIMS_MAP.md](./CLAIMS_MAP.md)).
4. **Accidental dry-run mix** — if traces contain `"status": "dry_run"`, exclude from scoring; prefer abort and re-run after cleanup.

After stop: document `n` completed, reason, and whether scorers may run (partial only).

---

## 5. Post-run

**v0 harness**

```bash
python3 scripts/score_asr.py
python3 scripts/score_utility.py
```

Archive stdout JSON with traces. Update [STATUS.md](./STATUS.md) with facts only (date, model, n) — not invented rates. If `n < 20` per split, do **not** label as full v0 Phase A pilot.

**Research paired runs**

Use the frozen protocol scripts and output roots documented in `config/` and [STATUS.md](./STATUS.md). Score with the paired metric tooling (e.g. `scripts/score_p4_3_paired_metrics.py`) on the immutable run directory. Do not substitute missing run IDs.

---

## 6. Explicit non-goals

- This gate does **not** by itself upgrade evidence to Level B ([`RESULTS_EVIDENCE.md`](../paper/RESULTS_EVIDENCE.md)).
- This gate does **not** override [CLAIMS_MAP.md](./CLAIMS_MAP.md) — refusals are not defense wins; sibling Track A/B numbers stay out of AIB tables.

---

## 7. Operator pointer

After sign-off: [PHASE_A_PILOT.md](./PHASE_A_PILOT.md) (v0 harness). Day-to-day offline: [START_HERE.md](./START_HERE.md).
