# Phase A pilot runbook (v0 harness)

Operator checklist for a **live LLM pilot** on the frozen **v0** bench (20 attack + 20 benign twins, offline mock tools). This is **not** the P4.2/P3 paired research protocol and **not** a Level B study.

**Before live runs:** human sign-off in [LIVE_EVAL_GATE.md](./LIVE_EVAL_GATE.md). **Claims:** [CLAIMS_MAP.md](./CLAIMS_MAP.md). **Overview:** [START_HERE.md](./START_HERE.md).

**Note:** Level A descriptive evidence on `main` (e.g. `p42-primary-d0-d2-20260921T173736Z-controlled`) lives under frozen paired run trees — see [STATUS.md](./STATUS.md) and [`../paper/RESULTS_EVIDENCE.md`](../paper/RESULTS_EVIDENCE.md). This runbook is for the **v0** `results/traces/` harness path only.

## Scope reminder

| In scope | Out of scope |
|----------|----------------|
| Live harness traces under `results/traces/` | Claiming Level B or defense efficacy |
| ASR / utility from `score_*.py` JSON only | Real email or network I/O |
| Auditable trace files | Citing rates without traces or run IDs |

## Gate: API key

Live runs require **`AIB_LLM_API_KEY`** (see `.env.example`). Without it, stop after **offline green** (validate + pytest + dry-run).

```bash
cp .env.example .env
# Edit .env — set AIB_LLM_API_KEY (never commit .env)
```

Optional: `AIB_LLM_BASE_URL`, `AIB_LLM_MODEL`. Empty key → harness must not call the LLM.

---

## Step 0 — Install

Python **3.10+** recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python3 -m pip install -e ".[dev]"
```

---

## Step 1 — Validate dataset (offline)

```bash
python3 scripts/validate_episodes.py
```

**Pass:** JSON with `"ok": true`, `"errors": 0`.

---

## Step 2 — Unit tests (offline)

```bash
python3 -m pytest
```

**Pass:** all tests green.

---

## Step 3 — Harness dry-run (offline, no key)

```bash
python3 scripts/run_agent.py --id atk_002 --dry-run
python3 scripts/run_agent.py --smoke --dry-run
python3 scripts/run_batch.py --split all --dry-run --limit 4
```

**Pass:** exit 0; trace JSON includes `"status": "dry_run"`.

Dry-run traces are **pipeline checks only**. Before live scoring, clear stale traces:

```bash
rm -f results/traces/*.json
```

---

## Step 4 — Smoke live (requires key)

```bash
python3 scripts/run_agent.py --id atk_002
python3 scripts/run_agent.py --id ben_002
```

**Pass:** traces with `"status": "ok"` (or `"max_steps"` / `"error"` — inspect; do not invent labels).

```bash
python3 scripts/run_agent.py --smoke
```

---

## Step 5 — Full v0 batch (requires key)

```bash
python3 scripts/run_batch.py --split all
```

Expect **40** ids (`atk_002`–`atk_021`, `ben_002`–`ben_021`). `atk_001` / `ben_001` are format demos only.

Rehearsal (partial):

```bash
python3 scripts/run_batch.py --split all --limit 4
```

---

## Step 6 — Score (live traces only)

```bash
python3 scripts/score_asr.py
python3 scripts/score_utility.py
```

### When output is **not** an evaluation result

- **`n`: 0** and **`rate`: null** — no traces for that split. Do not cite ASR or utility.
- **Partial traces** — partial `n` only; not full v0 pilot unless 20+20 live traces exist.
- **Dry-run traces** — scorers do not distinguish `dry_run` from live; clear before scoring (Step 3).

Record scorer JSON verbatim with model + date. Never hand-enter percentages.

---

## Step 7 — Archive evidence

- Keep `results/traces/*.json` locally (gitignored).
- Store scorer stdout alongside traces.
- Update [STATUS.md](./STATUS.md) with factual v0 pilot state only — do not overwrite Level A run inventory.

---

## Quick reference

```bash
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -e ".[dev]"
python3 scripts/validate_episodes.py
python3 -m pytest
python3 scripts/run_agent.py --smoke --dry-run
cp .env.example .env   # set AIB_LLM_API_KEY
rm -f results/traces/*.json
python3 scripts/run_agent.py --smoke
python3 scripts/run_batch.py --split all
python3 scripts/score_asr.py | tee results/asr_report.json
python3 scripts/score_utility.py | tee results/utility_report.json
```

See also: [RUNBOOK.md](./RUNBOOK.md), [CHECKLIST.md](./CHECKLIST.md).
