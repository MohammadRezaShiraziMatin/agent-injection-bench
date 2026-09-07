#!/usr/bin/env python3
"""Minimal batch runner: iterate seed episode ids, write traces, continue on error.

Prints ok/error/max_steps counts only. Does NOT compute or claim ASR/utility.
Uses D0 undefended prompt by default. Requires a live API key (see .env.example).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.config import LLMConfigError, config_from_env  # noqa: E402
from agent.errors import EpisodeLoadError, LLMError  # noqa: E402
from agent.llm import OpenAICompatibleClient  # noqa: E402
from agent.load import load_episode_by_id  # noqa: E402
from agent.loop import DEFAULT_PROMPT_ID, run_episode  # noqa: E402
from agent.traces import (  # noqa: E402
    RESULTS_TRACES_DIR,
    default_trace_path,
    make_run_id,
    write_manifest,
    write_trace,
)
from scripts._common import EPISODES_DIR, load_episodes  # noqa: E402


def _seed_ids() -> list[str]:
    """Ids under data/episodes/ only (not examples/). Sorted."""
    episodes = load_episodes([EPISODES_DIR])
    ids = [str(ep["id"]) for ep in episodes if isinstance(ep.get("id"), str)]
    return sorted(set(ids))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ids",
        nargs="*",
        default=None,
        help="Episode ids to run (default: all under data/episodes/).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=RESULTS_TRACES_DIR,
        help="Trace directory (default: results/traces/).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Bound the tool loop (default: AIB_LLM_MAX_STEPS or 6).",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Exit on first execution_status=error (default: continue).",
    )
    parser.add_argument(
        "--prompt-id",
        default=DEFAULT_PROMPT_ID,
        help="Prompt condition id (default: d0 = undefended baseline).",
    )
    args = parser.parse_args()

    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    ids = list(args.ids) if args.ids else _seed_ids()
    if not ids:
        print("No episode ids found under data/episodes/.", file=sys.stderr)
        return 1

    try:
        config = config_from_env(require_key=True)
    except LLMConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.max_steps is not None:
        config = replace(config, max_steps=args.max_steps)
    client = OpenAICompatibleClient(config)
    batch_run_id = make_run_id(model=config.model, episode_id="batch")
    prompt_id = args.prompt_id

    counts = {"ok": 0, "error": 0, "max_steps": 0, "other": 0, "load_failed": 0}
    results: list[dict] = []

    for episode_id in ids:
        try:
            episode = load_episode_by_id(episode_id)
        except EpisodeLoadError as exc:
            print(f"load_failed {episode_id}: {exc}", file=sys.stderr)
            counts["load_failed"] += 1
            results.append({"episode_id": episode_id, "execution_status": "load_failed"})
            if args.stop_on_error:
                break
            continue
        print(f"=== batch {episode_id} ===", file=sys.stderr)
        try:
            trace = run_episode(
                episode,
                client=client,
                config=config,
                max_steps=args.max_steps,
                run_id=batch_run_id,
                prompt_id=prompt_id,
            )
        except LLMError as exc:
            print(f"error {episode_id}: {exc}", file=sys.stderr)
            status = "error"
            counts["error"] += 1
            results.append(
                {"episode_id": episode_id, "execution_status": status, "error": str(exc)}
            )
            if args.stop_on_error:
                break
            continue
        status = str(trace.get("execution_status") or "other")
        if status in counts:
            counts[status] += 1
        else:
            counts["other"] += 1
        path = default_trace_path(str(trace.get("episode_id") or episode_id), out_dir)
        write_trace(trace, path)
        print(f"wrote {path} status={status}", file=sys.stderr)
        results.append(
            {
                "episode_id": episode_id,
                "execution_status": status,
                "trace_path": str(path),
            }
        )
        if status == "error" and args.stop_on_error:
            break

    statuses = [str(r.get("execution_status")) for r in results]
    manifest_path = write_manifest(
        batch_run_id,
        episode_ids=[str(r.get("episode_id")) for r in results],
        model=config.model,
        temperature=config.temperature,
        seed=config.seed,
        prompt_id=prompt_id,
        defense_condition="d0" if prompt_id == "d0" else prompt_id,
        statuses=statuses,
        traces_dir=str(out_dir),
        note=(
            "Batch run counts only. Not ASR/utility. "
            "D0 = undefended baseline. Skip execution_status=error when scoring."
        ),
    )
    print(f"wrote manifest {manifest_path}", file=sys.stderr)

    summary = {
        "batch": True,
        "run_id": batch_run_id,
        "prompt_id": prompt_id,
        "n_requested": len(ids),
        "n_attempted": len(results),
        "counts": counts,
        "results": results,
        "manifest": str(manifest_path),
        "note": (
            "Run counts only. Not ASR, utility, or a scientific claim. "
            "Do not score execution_status=error traces as attack success."
        ),
    }
    print(json.dumps(summary, indent=2))
    return 0 if counts["error"] == 0 and counts["load_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
