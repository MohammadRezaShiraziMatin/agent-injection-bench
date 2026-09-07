#!/usr/bin/env bash
# Phase C matrix: models × baselines {d0,d1} × K repeats (D2 external only).
# Usage (repo root):
#   export AIB_LLM_API_KEY=...
#   bash scripts/phase_c_matrix.sh
# Cheap:
#   AIB_PHASE_C_SMOKE_ONLY=1 bash scripts/phase_c_matrix.sh
# Env:
#   MODELS=gpt-4o-mini,gpt-4o
#   BASELINES=d0,d1
#   K=3
#   AIB_LLM_TEMPERATURE=0
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [[ -z "$line" || "$line" != *=* ]] && continue
    key="${line%%=*}"
    val="${line#*=}"
    val="${val%\"}"; val="${val#\"}"
    val="${val%\'}"; val="${val#\'}"
    if [[ -n "$key" && -z "${!key:-}" ]]; then
      export "$key=$val"
    fi
  done < .env
fi

KEY="${AIB_LLM_API_KEY:-${OPENAI_API_KEY:-}}"
if [[ -z "$KEY" ]]; then
  echo "Phase C requires AIB_LLM_API_KEY or OPENAI_API_KEY." >&2
  exit 2
fi
export AIB_LLM_API_KEY="$KEY"
export AIB_LLM_TEMPERATURE="${AIB_LLM_TEMPERATURE:-0}"

MODELS_CSV="${MODELS:-gpt-4o-mini,gpt-4o}"
BASELINES_CSV="${BASELINES:-d0,d1}"
K="${K:-3}"
SMOKE_ONLY="${AIB_PHASE_C_SMOKE_ONLY:-0}"
PLAN="$ROOT/results/phase_c_plan.json"
mkdir -p "$ROOT/results"

IFS=',' read -r -a MODELS_ARR <<<"$MODELS_CSV"
IFS=',' read -r -a BASELINES_ARR <<<"$BASELINES_CSV"

echo "Phase C matrix: models=${MODELS_CSV} baselines=${BASELINES_CSV} K=${K} temp=${AIB_LLM_TEMPERATURE} smoke_only=${SMOKE_ONLY}" >&2
echo "D2 (ADAPTI) is external-only — not executed by this script." >&2

# Write plan before runs
python3 -c '
import json, sys
from pathlib import Path
plan_path, models_csv, baselines_csv, k, smoke, temp = sys.argv[1:7]
models = [m.strip() for m in models_csv.split(",") if m.strip()]
baselines = [b.strip() for b in baselines_csv.split(",") if b.strip()]
k = int(k)
cells = []
for model in models:
    for baseline in baselines:
        for rep in range(1, k + 1):
            cells.append({
                "model": model,
                "baseline": baseline,
                "prompt_id": baseline,
                "repeat": rep,
                "run_id": None,
                "status": "planned",
            })
payload = {
    "phase": "C",
    "pilot": True,
    "publication_ready": False,
    "temperature": float(temp),
    "models": models,
    "baselines": baselines,
    "k": k,
    "smoke_only": smoke == "1",
    "d2": "external_only",
    "cells": cells,
    "note": "Plan written before execution. run_ids filled after each cell. Not ASR.",
}
Path(plan_path).parent.mkdir(parents=True, exist_ok=True)
Path(plan_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(f"wrote {plan_path}")
' "$PLAN" "$MODELS_CSV" "$BASELINES_CSV" "$K" "$SMOKE_ONLY" "$AIB_LLM_TEMPERATURE"

extract_run_id() {
  python3 -c '
import json, re, sys
text = sys.stdin.read()
decoder = json.JSONDecoder()
idx = 0
last = None
while idx < len(text):
    while idx < len(text) and text[idx] not in "{[":
        idx += 1
    if idx >= len(text):
        break
    try:
        obj, end = decoder.raw_decode(text, idx)
    except json.JSONDecodeError:
        idx += 1
        continue
    idx = end
    if isinstance(obj, dict) and obj.get("run_id"):
        last = obj["run_id"]
if last:
    print(last); raise SystemExit(0)
m = re.findall(r"wrote manifest .*/([^/\s]+)\.json", text)
if m:
    print(m[-1]); raise SystemExit(0)
raise SystemExit("could not parse run_id")
'
}

quota_fail() {
  echo "$1" | grep -Eqi 'insufficient_quota|Error code: 429|"code"[[:space:]]*:[[:space:]]*"insufficient_quota"|HTTP 429'
}

update_plan_cell() {
  python3 -c '
import json, sys
from pathlib import Path
plan_path, model, baseline, rep, run_id, status = sys.argv[1:7]
plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
for cell in plan["cells"]:
    if cell["model"] == model and cell["baseline"] == baseline and int(cell["repeat"]) == int(rep):
        cell["run_id"] = run_id or None
        cell["status"] = status
        break
Path(plan_path).write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
' "$PLAN" "$1" "$2" "$3" "$4" "$5"
}

# Patch last written manifest with repeat index (best-effort)
stamp_repeat() {
  local run_id="$1"
  local rep="$2"
  python3 -c '
import json, sys
from pathlib import Path
root, run_id, rep = sys.argv[1:4]
safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in run_id)
path = Path(root) / "results" / "manifests" / f"{safe}.json"
if path.is_file():
    data = json.loads(path.read_text(encoding="utf-8"))
    data["repeat"] = int(rep)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
' "$ROOT" "$run_id" "$rep"
}

overall_rc=0
for model in "${MODELS_ARR[@]}"; do
  for baseline in "${BASELINES_ARR[@]}"; do
    for ((rep=1; rep<=K; rep++)); do
      export AIB_LLM_MODEL="$model"
      export AIB_LLM_TEMPERATURE=0
      export AIB_PROMPT_ID="$baseline"
      echo "=== Phase C cell model=${model} baseline=${baseline} repeat=${rep} ===" >&2
      log="$(mktemp)"
      set +e
      if [[ "$SMOKE_ONLY" == "1" ]]; then
        python3 scripts/run_agent.py --smoke --prompt-id "$baseline" >"$log" 2>&1
      else
        python3 scripts/run_batch.py --prompt-id "$baseline" >"$log" 2>&1
      fi
      rc=$?
      set -e
      blob="$(cat "$log")"
      if quota_fail "$blob"; then
        echo "Phase C hit quota/429 on model=${model} baseline=${baseline} repeat=${rep}" >&2
        echo "$blob" >&2
        update_plan_cell "$model" "$baseline" "$rep" "" "quota_error"
        rm -f "$log"
        overall_rc=42
        break 3
      fi
      if [[ "$rc" -ne 0 ]]; then
        echo "Phase C cell failed rc=${rc}" >&2
        echo "$blob" >&2
        update_plan_cell "$model" "$baseline" "$rep" "" "failed"
        overall_rc=$rc
        rm -f "$log"
        continue
      fi
      run_id="$(printf '%s' "$blob" | extract_run_id)" || run_id=""
      if [[ -z "$run_id" ]]; then
        update_plan_cell "$model" "$baseline" "$rep" "" "parse_error"
        overall_rc=1
        rm -f "$log"
        continue
      fi
      stamp_repeat "$run_id" "$rep"
      update_plan_cell "$model" "$baseline" "$rep" "$run_id" "ok"
      echo "cell ok run_id=${run_id}" >&2
      rm -f "$log"
    done
  done
done

echo "=== Phase C aggregate ===" >&2
python3 scripts/aggregate_phase_c.py --plan "$PLAN" || true

if [[ "$overall_rc" -eq 42 ]]; then
  exit 1
fi
exit "$overall_rc"
