#!/usr/bin/env python3
"""Minimal batch runner: iterate seed episode ids, write traces, continue on error.

Traces: results/traces/<run_id>/<episode_id>.json (no overwrite unless --force).
Prints ok/error/max_steps counts only. Does NOT claim ASR/utility.
Uses D0 undefended prompt by default.
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
    TraceExistsError,
    default_trace_path,
    make_run_id,
    write_manifest,
    write_trace,
)
from scripts._common import EPISODES_DIR, load_episodes  # noqa: E402


def _seed_ids() -> list[str]:
    episodes = load_episodes([EPISODES_DIR])
    ids = [str(ep["id"]) for ep in episodes if isinstance(ep.get("id"), str)]
    return sorted(set(ids))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", nargs="*", default=None)
    parser.add_argument("--out-dir", type=Path, default=RESULTS_TRACES_DIR)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--stop-on-error", action="store_true")
    parser.add_argument("--prompt-id", default=DEFAULT_PROMPT_ID)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting existing traces/manifest for this run_id.",
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
    force = args.force
    run_traces_dir = out_dir / batch_run_id

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
        path = default_trace_path(
            str(trace.get("episode_id") or episode_id), out_dir, run_id=batch_run_id
        )
        try:
            write_trace(trace, path, force=force)
        except TraceExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 3
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
    try:
        manifest_path = write_manifest(
            batch_run_id,
            episode_ids=[str(r.get("episode_id")) for r in results],
            model=config.model,
            provider=config.provider,
            base_url=config.base_url,
            temperature=config.temperature,
            seed=config.seed,
            prompt_id=prompt_id,
            defense_condition="d0" if prompt_id == "d0" else prompt_id,
            statuses=statuses,
            traces_dir=str(run_traces_dir),
            note=(
                "Batch run counts only. Not ASR/utility. "
                "D0 = undefended baseline. Skip execution_status=error when scoring."
            ),
            force=force,
        )
    except TraceExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 3
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
