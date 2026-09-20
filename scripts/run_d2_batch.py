#!/usr/bin/env python3
"""D2 batch runner: AdaptiGuard-gated tool loop, AIB mock execution, d2 traces."""

from __future__ import annotations

import argparse
import json
import os
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
from agent.loop import DEFAULT_PROMPT_PATH, PROMPTS_DIR  # noqa: E402
from agent.traces import (  # noqa: E402
    RESULTS_TRACES_DIR,
    TraceExistsError,
    default_trace_path,
    make_run_id,
    write_trace,
)
from d2_bridge.config import D2DefenseConfig, DEFAULT_DEFENSE_LEVEL_PROVISIONAL  # noqa: E402
from d2_bridge.loop import run_d2_episode  # noqa: E402
from d2_bridge.manifest import write_d2_manifest  # noqa: E402
from scripts._common import EPISODES_DIR, load_episodes  # noqa: E402


def _seed_ids() -> list[str]:
    episodes = load_episodes([EPISODES_DIR])
    ids = [str(ep["id"]) for ep in episodes if isinstance(ep.get("id"), str)]
    return sorted(set(ids))


def _defense_config_from_args(args: argparse.Namespace) -> D2DefenseConfig:
    level = args.defense_level
    if level is None:
        level = int(os.environ.get("AIB_D2_DEFENSE_LEVEL", DEFAULT_DEFENSE_LEVEL_PROVISIONAL))
    provisional = args.defense_level is None and os.environ.get("AIB_D2_DEFENSE_LEVEL") is None
    return D2DefenseConfig(
        defense_level=level,
        defense_level_provisional=provisional or args.defense_level_provisional,
        base_prompt_id=args.base_prompt_id,
        deny_message_mode=args.deny_message_mode,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", nargs="*", default=None)
    parser.add_argument("--out-dir", type=Path, default=RESULTS_TRACES_DIR)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--stop-on-error", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--defense-level",
        type=int,
        default=None,
        help="AdaptiGuard defense_level (default: provisional 0 unless AIB_D2_DEFENSE_LEVEL set).",
    )
    parser.add_argument(
        "--defense-level-provisional",
        action="store_true",
        help="Mark defense_level as provisional in manifest even when explicitly set.",
    )
    parser.add_argument(
        "--base-prompt-id",
        default="d0",
        help="System prompt id (default d0 → prompts/d0_undefended.txt).",
    )
    parser.add_argument(
        "--deny-message-mode",
        default="tool_denied_literal",
        choices=["tool_denied_literal", "empty", "default"],
    )
    parser.add_argument(
        "--skip-lock-verify",
        action="store_true",
        help="Skip detector-lock SHA verification (not for production D2 runs).",
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

    defense_config = _defense_config_from_args(args)
    client = OpenAICompatibleClient(config)
    batch_run_id = make_run_id(model=config.model, episode_id="d2_batch")
    force = args.force
    run_traces_dir = out_dir / batch_run_id

    prompt_path = DEFAULT_PROMPT_PATH
    if defense_config.base_prompt_id != "d0":
        prompt_path = PROMPTS_DIR / f"{defense_config.base_prompt_id}_undefended.txt"

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
        print(f"=== d2 batch {episode_id} ===", file=sys.stderr)
        try:
            trace = run_d2_episode(
                episode,
                client=client,
                config=config,
                max_steps=args.max_steps,
                run_id=batch_run_id,
                defense_config=defense_config,
                verify_lock=not args.skip_lock_verify,
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
        manifest_path = write_d2_manifest(
            batch_run_id,
            episode_ids=[str(r.get("episode_id")) for r in results],
            model=config.model,
            provider=config.provider,
            base_url=config.base_url,
            temperature=config.temperature,
            seed=config.seed,
            statuses=statuses,
            traces_dir=str(run_traces_dir),
            defense_config=defense_config,
            prompt_path=prompt_path,
            force=force,
        )
    except TraceExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 3

    summary = {
        "batch": True,
        "run_id": batch_run_id,
        "defense_condition": "d2",
        "n_requested": len(ids),
        "n_attempted": len(results),
        "counts": counts,
        "results": results,
        "manifest": str(manifest_path),
        "note": "D2 batch counts only. Score with unchanged score_asr/score_utility.",
    }
    print(json.dumps(summary, indent=2))
    return 0 if counts["error"] == 0 and counts["load_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
