# Live eval gate (design only)

This document defines **human and technical gates** before spending API budget on live LLM runs in agent-injection-bench. It mirrors discipline used in sibling Adaptive/AdaptiGuard work but **does not authorize** a live run by itself — an explicit human sign-off is required.

**Default: API=0.** Contributors and CI should stay offline unless this gate is satisfied.

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
| **Purpose** | e.g. “Phase A v0 full batch” or “smoke only (2 eps)” |
| **Episode scope** | Exact ids or `--split` + `--limit` |
| **Model pin** | `AIB_LLM_MODEL` + provider |
| **Budget cap** | Max spend or max episodes × estimated tokens |
| **Target ≠ Judge** | Confirm UUT model id ≠ any automated judge endpoint used for auxiliary labels |
| **Cache policy** | Confirm cache disabled for provider/client (document how) |
| **Trace hygiene** | Plan to `rm -f results/traces/*.json` before live batch if dry-run files exist |

Sign-off may be a ticket, email, or lab log entry — not committed secrets.

---

## 3. API key handling

- Copy `.env.example` → `.env`; set `AIB_LLM_API_KEY` only after sign-off.
- Never commit `.env` or keys.
- Revoke or rotate keys after pilot if policy requires.

Optional overrides: `AIB_LLM_BASE_URL`, `AIB_LLM_MODEL`.

---

## 4. Stop rules (during live run)

Stop immediately and preserve partial traces if:

1. **Budget exceeded** — halt batch; do not silently continue.
2. **Schema / harness error** — fix offline; do not “patch forward” mid-batch without new sign-off.
3. **Provider outage or rate limit storm** — pause; partial `n` is **partial**, not full pilot ([CLAIMS_MAP.md](./CLAIMS_MAP.md)).
4. **Accidental dry-run mix** — if traces contain `"status": "dry_run"`, exclude from scoring; prefer abort and re-run after cleanup.

After stop: document `n` completed, reason, and whether scorers may be run (partial only).

---

## 5. Post-run (scoring allowed only for live traces)

```bash
python3 scripts/score_asr.py
python3 scripts/score_utility.py
```

Archive stdout JSON with traces. Update [STATUS.md](./STATUS.md) with facts only (date, model, n).

If `n < 20` per split, do **not** label as full v0 Phase A pilot.

---

## 6. Explicit non-goals

- This gate does **not** approve AdaptiGuard defense experiments (see defense repo + [ADAPTI_GUARD_BRIDGE.md](./ADAPTI_GUARD_BRIDGE.md)).
- This gate does **not** override [CLAIMS_MAP.md](./CLAIMS_MAP.md) — refusals are not defense wins; sibling Track A/B numbers stay out of AIB tables.

---

## 7. Operator pointer

After sign-off, execute [PHASE_A_PILOT.md](./PHASE_A_PILOT.md). For day-to-day offline work, use [START_HERE.md](./START_HERE.md).
