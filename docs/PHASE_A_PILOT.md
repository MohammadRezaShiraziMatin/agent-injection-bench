# Phase A pilot runbook (v0)

Operator checklist for the **first live LLM pilot** on the frozen v0 bench (20 attack + 20 benign twins, offline mock tools only). This is **not** a defense evaluation and **not** ADAPTI-GUARD.

## Scope reminder

| In scope | Out of scope |
|----------|----------------|
| Live harness traces under `results/traces/` | Defenses, ADAPTI-GUARD code |
| ASR / utility from scorer JSON only | Real email or network I/O |
| Auditable trace files | Citing rates without traces |

## Gate: API key

Live runs require **`AIB_LLM_API_KEY`** (see `.env.example`). Without it, stop after **offline green** (validate + pytest + dry-run).

```bash
cp .env.example .env
# Edit .env — set AIB_LLM_API_KEY (never commit .env)
```

Optional overrides: `AIB_LLM_BASE_URL`, `AIB_LLM_MODEL`. If `AIB_LLM_API_KEY` is empty, the harness must not call the LLM.

---

## Step 0 — Install

Python **3.10+** recommended.

```bash
cd agent-injection-bench
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python3 -m pip install -e ".[dev]"
```

Use `python3` (or `python` if it points to 3.10+).

---

## Step 1 — Validate dataset (offline)

```bash
python3 scripts/validate_episodes.py
```

**Pass:** JSON with `"ok": true`, `"n": 42`, `"errors": 0`.

---

## Step 2 — Unit tests (offline)

```bash
python3 -m pytest
```

**Pass:** all tests green (14 in v0 scaffold).

---

## Step 3 — Harness dry-run (offline, no key)

Confirms import path, episode load, mock tools, and trace write path **without** LLM calls.

```bash
python3 scripts/run_agent.py --id atk_002 --dry-run
python3 scripts/run_agent.py --smoke --dry-run
python3 scripts/run_batch.py --split all --dry-run --limit 4
```

**Pass:** each command exits 0; trace JSON includes `"status": "dry_run"`.

Dry-run traces are **pipeline checks only**. Do **not** treat scorer output over dry-run traces as a pilot result. Before live scoring, either delete stale traces or overwrite them with live runs:

```bash
rm -f results/traces/*.json
# .gitkeep remains; traces stay gitignored
```

---

## Step 4 — Smoke live (requires key)

After `.env` is set:

```bash
python3 scripts/run_agent.py --id atk_002
python3 scripts/run_agent.py --id ben_002
```

**Pass:** traces written with `"status": "ok"` (or `"max_steps"` / `"error"` — inspect trace; do not invent labels).

Optional pipeline smoke (two episodes):

```bash
python3 scripts/run_agent.py --smoke
```

---

## Step 5 — Full v0 batch (requires key)

```bash
python3 scripts/run_batch.py --split all
```

Expect **40** episode ids (`atk_002`–`atk_021`, `ben_002`–`ben_021`). Examples `atk_001` / `ben_001` are format demos only and are not in the batch split dirs.

For a capped rehearsal (still live LLM, not a full eval):

```bash
python3 scripts/run_batch.py --split all --limit 4
```

---

## Step 6 — Score (only with live traces present)

```bash
python3 scripts/score_asr.py
python3 scripts/score_utility.py
```

### When output is **not** an evaluation result

- **`n`: 0** and **`rate`: null** — no trace files found for that split. **Do not cite** ASR or utility.
- **Partial traces** (e.g. only 4 attack files) — scorers report `n` equal to the number of traces on disk; that is a **partial** count, not the v0 full-pilot metric unless all 20+20 live traces exist.
- **Dry-run traces** — scorers do not distinguish `dry_run` from live; clear dry-run files before scoring a live pilot (Step 3).

A **v0 Phase A pilot report** should record scorer JSON verbatim (or archived copies) and note model + date. Never hand-enter ASR/utility percentages.

---

## Step 7 — Archive evidence

- Keep `results/traces/*.json` locally (gitignored).
- Store scorer stdout JSON alongside traces for audit.
- Update `docs/STATUS.md` only with factual state (e.g. “40 live traces scored on YYYY-MM-DD”) — not invented numbers.

---

## Quick reference (Matin — live pilot on a machine with key)

```bash
cd agent-injection-bench
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
