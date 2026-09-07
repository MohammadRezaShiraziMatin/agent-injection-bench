#!/usr/bin/env bash
# Phase A dual-model pilot runner (D0). Honest traces + scores only — no invented metrics.
# Usage (from repo root):
#   export AIB_LLM_API_KEY=...
#   bash scripts/phase_a_pilot.sh
# Optional:
#   AIB_PHASE_A_MODEL1=gpt-4o-mini AIB_PHASE_A_MODEL2=gpt-4o
#   AIB_PHASE_A_SMOKE_ONLY=1   # smoke model1 then stop (debug / quota check)
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
  echo "Phase A requires AIB_LLM_API_KEY or OPENAI_API_KEY." >&2
  exit 2
fi
export AIB_LLM_API_KEY="$KEY"
export AIB_LLM_TEMPERATURE="${AIB_LLM_TEMPERATURE:-0}"

MODEL1="${AIB_PHASE_A_MODEL1:-gpt-4o-mini}"
MODEL2="${AIB_PHASE_A_MODEL2:-gpt-4o}"
if [[ "$MODEL1" == "$MODEL2" ]]; then
  echo "Phase A needs two distinct model ids. Set AIB_PHASE_A_MODEL1 and AIB_PHASE_A_MODEL2." >&2
  echo "Defaults are gpt-4o-mini and gpt-4o (note: gpt-4o incurs higher cost)." >&2
  exit 2
fi

SMOKE_ONLY="${AIB_PHASE_A_SMOKE_ONLY:-0}"
OUT_SUMMARY="$ROOT/results/phase_a_summary.json"
mkdir -p "$ROOT/results"

echo "Phase A: temperature=${AIB_LLM_TEMPERATURE} models=${MODEL1} + ${MODEL2}" >&2
echo "Note: AIB_LLM_SEED is best-effort; many APIs ignore seed." >&2

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
    print(last)
    raise SystemExit(0)
m = re.findall(r"wrote manifest .*/([^/\s]+)\.json", text)
if m:
    print(m[-1])
    raise SystemExit(0)
raise SystemExit("could not parse run_id from runner output")
'
}

quota_fail() {
  local blob="$1"
  echo "$blob" | grep -Eqi 'insufficient_quota|Error code: 429|"code"[[:space:]]*:[[:space:]]*"insufficient_quota"|HTTP 429'
}

# Returns: 0 ok, 42 quota, other failure
run_one_model() {
  local model="$1"
  export AIB_LLM_MODEL="$model"
  export AIB_LLM_TEMPERATURE=0
  echo "=== Phase A model=${model} smoke ===" >&2
  local smoke_log batch_log
  smoke_log="$(mktemp)"
  batch_log="$(mktemp)"
  set +e
  python3 scripts/run_agent.py --smoke >"$smoke_log" 2>&1
  local smoke_rc=$?
  set -e
  local smoke_blob
  smoke_blob="$(cat "$smoke_log")"
  if quota_fail "$smoke_blob"; then
    echo "Phase A smoke hit quota/429 for model=${model}. Stopping." >&2
    echo "$smoke_blob" >&2
    rm -f "$smoke_log" "$batch_log"
    return 42
  fi
  if [[ "$smoke_rc" -ne 0 ]]; then
    echo "Phase A smoke failed (rc=${smoke_rc}) for model=${model}." >&2
    echo "$smoke_blob" >&2
    rm -f "$smoke_log" "$batch_log"
    return "$smoke_rc"
  fi
  local smoke_run_id=""
  smoke_run_id="$(printf '%s' "$smoke_blob" | extract_run_id)" || smoke_run_id=""
  echo "smoke run_id=${smoke_run_id}" >&2

  if [[ "$SMOKE_ONLY" == "1" ]]; then
    python3 -c '
import json, sys
from pathlib import Path
out, model, smoke_run_id = sys.argv[1], sys.argv[2], sys.argv[3]
payload = {
    "phase": "A",
    "pilot": True,
    "publication_ready": False,
    "temperature": 0,
    "seed_note": "AIB_LLM_SEED is best-effort; many OpenAI-compatible APIs ignore or partially honor seed.",
    "asr_level": "L0_tool_name_only",
    "models": [{
        "model": model,
        "smoke_run_id": smoke_run_id or None,
        "smoke_only": True,
        "note": "Stopped after smoke (AIB_PHASE_A_SMOKE_ONLY=1). Not a full Phase A result.",
    }],
    "message": "Partial Phase A (smoke only). Not ASR/utility evaluation.",
}
Path(out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
' "$OUT_SUMMARY" "$model" "${smoke_run_id:-}"
    rm -f "$smoke_log" "$batch_log"
    return 0
  fi

  echo "=== Phase A model=${model} batch ===" >&2
  set +e
  python3 scripts/run_batch.py >"$batch_log" 2>&1
  local batch_rc=$?
  set -e
  local batch_blob
  batch_blob="$(cat "$batch_log")"
  if quota_fail "$batch_blob"; then
    echo "Phase A batch hit quota/429 for model=${model}." >&2
    echo "$batch_blob" >&2
    rm -f "$smoke_log" "$batch_log"
    return 42
  fi
  local batch_run_id=""
  batch_run_id="$(printf '%s' "$batch_blob" | extract_run_id)" || true
  if [[ -z "${batch_run_id:-}" ]]; then
    echo "Could not parse batch run_id" >&2
    echo "$batch_blob" >&2
    rm -f "$smoke_log" "$batch_log"
    return 1
  fi
  echo "batch run_id=${batch_run_id} rc=${batch_rc}" >&2
  local traces_dir="$ROOT/results/traces/${batch_run_id}"
  if [[ ! -d "$traces_dir" ]]; then
    echo "Missing traces dir: $traces_dir" >&2
    rm -f "$smoke_log" "$batch_log"
    return 1
  fi

  local asr_file util_file
  asr_file="$(mktemp)"
  util_file="$(mktemp)"
  python3 scripts/score_asr.py --level 0 --traces-dir "$traces_dir" >"$asr_file"
  python3 scripts/score_utility.py --traces-dir "$traces_dir" >"$util_file"

  python3 -c '
import json, os, sys
from pathlib import Path
model, smoke_run_id, batch_run_id, batch_rc, asr_path, util_path, partial = sys.argv[1:8]
asr = json.loads(Path(asr_path).read_text(encoding="utf-8"))
util = json.loads(Path(util_path).read_text(encoding="utf-8"))
row = {
    "model": model,
    "smoke_run_id": smoke_run_id or None,
    "batch_run_id": batch_run_id,
    "batch_exit_code": int(batch_rc),
    "traces_dir": f"results/traces/{batch_run_id}",
    "asr_l0": {
        "n": asr.get("n"),
        "successes": asr.get("successes"),
        "rate": asr.get("rate"),
        "skipped": asr.get("skipped"),
        "message": asr.get("message"),
    },
    "utility": {
        "n": util.get("n"),
        "successes": util.get("successes"),
        "rate": util.get("rate"),
        "skipped": util.get("skipped"),
        "message": util.get("message"),
    },
}
path = Path(partial)
rows = json.loads(path.read_text(encoding="utf-8")) if path.is_file() and path.read_text(encoding="utf-8").strip() else []
rows.append(row)
path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
print(json.dumps(row, indent=2))
' "$model" "${smoke_run_id:-}" "$batch_run_id" "$batch_rc" "$asr_file" "$util_file" "$PHASE_A_PARTIAL"

  rm -f "$smoke_log" "$batch_log" "$asr_file" "$util_file"
  return 0
}

PARTIAL="$(mktemp)"
echo "[]" >"$PARTIAL"
export PHASE_A_PARTIAL="$PARTIAL"
trap 'rm -f "$PARTIAL"' EXIT

models=("$MODEL1" "$MODEL2")
if [[ "$SMOKE_ONLY" == "1" ]]; then
  models=("$MODEL1")
fi

overall_rc=0
for m in "${models[@]}"; do
  set +e
  run_one_model "$m"
  rc=$?
  set -e
  if [[ "$rc" -eq 42 ]]; then
    overall_rc=42
    break
  fi
  if [[ "$rc" -ne 0 ]]; then
    overall_rc=$rc
    if [[ "$SMOKE_ONLY" == "1" ]]; then
      break
    fi
  fi
done

if [[ "$SMOKE_ONLY" != "1" ]]; then
  python3 -c '
import json, sys
from pathlib import Path
out, partial, m1, m2, rc = sys.argv[1:6]
rows = json.loads(Path(partial).read_text(encoding="utf-8"))
payload = {
    "phase": "A",
    "pilot": True,
    "publication_ready": False,
    "defense_condition": "d0",
    "temperature": 0,
    "seed_note": (
        "AIB_LLM_SEED is optional and best-effort; many OpenAI-compatible APIs "
        "ignore or only partially honor seed. Do not claim bit-exact reproducibility "
        "from seed alone."
    ),
    "asr_level": "L0_tool_name_only",
    "models_requested": [m1, m2],
    "models": rows,
    "exit_code": int(rc),
    "message": (
        "Phase A pilot aggregate from disk scorers only. "
        "rate=null means undefined (e.g. N=0), not a measured zero. "
        "Not a published benchmark. No defense results."
    ),
}
Path(out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
print(f"wrote {out}", file=sys.stderr)
' "$OUT_SUMMARY" "$PARTIAL" "$MODEL1" "$MODEL2" "$overall_rc"
fi

if [[ "$overall_rc" -eq 42 ]]; then
  exit 1
fi
exit "$overall_rc"
