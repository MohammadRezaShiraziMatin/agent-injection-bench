#!/usr/bin/env python3
"""Run one episode through the Phase 2 LLM harness and write an auditable trace.

Uses only mock tools (search_docs, send_email). D0 undefended prompt by default.
Traces: results/traces/<run_id>/<episode_id>.json (no overwrite unless --force).
No defenses. Does not score ASR or utility.
"""

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
from agent.load import load_episode, load_episode_by_id  # noqa: E402
from agent.loop import DEFAULT_PROMPT_ID, run_episode  # noqa: E402
from agent.traces import (  # noqa: E402
    RESULTS_TRACES_DIR,
    TraceExistsError,
    default_trace_path,
    make_run_id,
    write_manifest,
    write_trace,
)


def _default_prompt_id() -> str:
    return (os.environ.get("AIB_PROMPT_ID") or DEFAULT_PROMPT_ID).strip() or DEFAULT_PROMPT_ID


def _print_trace(trace: dict) -> None:
    print(json.dumps({k: v for k, v in trace.items() if not str(k).startswith("_")}, indent=2))


def _write_trace_safe(trace: dict, path: Path, *, force: bool) -> None:
    try:
        write_trace(trace, path, force=force)
    except TraceExistsError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(3) from exc
    print(f"wrote {path}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode", type=Path, default=None)
    parser.add_argument("--id", dest="episode_id", default=None)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=RESULTS_TRACES_DIR,
        help="Root trace directory (default: results/traces/). Files go under <run_id>/.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Explicit trace path (single episode; still refuses overwrite without --force).",
    )
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument(
        "--prompt-id",
        "--prompt",
        dest="prompt_id",
        default=_default_prompt_id(),
        help="Prompt condition id (default: AIB_PROMPT_ID or d0).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting an existing trace/manifest path.",
    )
    args = parser.parse_args()

    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    prompt_id = args.prompt_id
    force = args.force

    if args.smoke:
        if args.dry_run:
            print("--smoke is a live pipeline check; omit --dry-run.", file=sys.stderr)
            return 2
        try:
            config = config_from_env(require_key=True)
        except LLMConfigError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if args.max_steps is not None:
            config = replace(config, max_steps=args.max_steps)
        batch_run_id = make_run_id(model=config.model, episode_id="smoke")
        client = OpenAICompatibleClient(config)
        run_traces_dir = out_dir / batch_run_id if not args.no_write else out_dir
        traces = []
        for episode_id in ("atk_002", "ben_002"):
            try:
                episode = load_episode_by_id(episode_id)
            except EpisodeLoadError as exc:
                print(str(exc), file=sys.stderr)
                return 1
            print(f"=== smoke {episode_id} ===", file=sys.stderr)
            trace = run_episode(
                episode,
                client=client,
                config=config,
                max_steps=args.max_steps,
                run_id=batch_run_id,
                prompt_id=prompt_id,
            )
            _print_trace(trace)
            if not args.no_write:
                path = default_trace_path(
                    str(trace.get("episode_id") or episode_id),
                    out_dir,
                    run_id=batch_run_id,
                )
                _write_trace_safe(trace, path, force=force)
            traces.append(trace)
        statuses = [str(t.get("execution_status")) for t in traces]
        if not args.no_write:
            try:
                manifest_path = write_manifest(
                    batch_run_id,
                    episode_ids=["atk_002", "ben_002"],
                    model=config.model,
                    provider=config.provider,
                    base_url=config.base_url,
                    temperature=config.temperature,
                    seed=config.seed,
                    prompt_id=prompt_id,
                    defense_condition="d0" if prompt_id == "d0" else prompt_id,
                    statuses=statuses,
                    traces_dir=str(run_traces_dir),
                    note="Smoke pipeline only. Not ASR/utility.",
                    force=force,
                )
            except TraceExistsError as exc:
                print(str(exc), file=sys.stderr)
                return 3
            print(f"wrote manifest {manifest_path}", file=sys.stderr)
        print(
            json.dumps(
                {
                    "smoke": True,
                    "run_id": batch_run_id,
                    "prompt_id": prompt_id,
                    "episodes": ["atk_002", "ben_002"],
                    "execution_status": statuses,
                    "note": "Pipeline verification only. Not ASR, utility, or a scientific result.",
                },
                indent=2,
            )
        )
        return 0 if all(s in {"ok", "max_steps"} for s in statuses) else 1

    if args.episode_id:
        try:
            episode = load_episode_by_id(args.episode_id)
        except EpisodeLoadError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    else:
        episode_path = args.episode or (ROOT / "examples" / "episode_attack_001.json")
        try:
            episode = load_episode(episode_path)
        except EpisodeLoadError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    try:
        if args.dry_run:
            trace = run_episode(
                episode, dry_run=True, max_steps=args.max_steps, prompt_id=prompt_id
            )
            _print_trace(trace)
            if not args.no_write:
                run_id = str(trace.get("run_id") or "dry_run")
                path = (
                    args.out
                    if args.out
                    else default_trace_path(
                        str(trace.get("episode_id") or episode.get("id") or "unknown"),
                        out_dir,
                        run_id=run_id,
                    )
                )
                if args.out and not path.is_absolute():
                    path = ROOT / path
                _write_trace_safe(trace, path, force=force)
            return 0

        try:
            config = config_from_env(require_key=True)
        except LLMConfigError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if args.max_steps is not None:
            config = replace(config, max_steps=args.max_steps)
        client = OpenAICompatibleClient(config)
        run_id = make_run_id(
            model=config.model, episode_id=str(episode.get("id") or "unknown")
        )
        trace = run_episode(
            episode,
            client=client,
            config=config,
            max_steps=args.max_steps,
            run_id=run_id,
            prompt_id=prompt_id,
        )
        _print_trace(trace)
        if not args.no_write:
            path = (
                args.out
                if args.out
                else default_trace_path(
                    str(trace.get("episode_id") or episode.get("id") or "unknown"),
                    out_dir,
                    run_id=run_id,
                )
            )
            if args.out and not Path(path).is_absolute():
                path = ROOT / path
            path = Path(path)
            _write_trace_safe(trace, path, force=force)
            run_traces_dir = str(path.parent)
            try:
                write_manifest(
                    run_id,
                    episode_ids=[str(episode.get("id") or "")],
                    model=config.model,
                    provider=config.provider,
                    base_url=config.base_url,
                    temperature=config.temperature,
                    seed=config.seed,
                    prompt_id=prompt_id,
                    defense_condition="d0" if prompt_id == "d0" else prompt_id,
                    statuses=[str(trace.get("execution_status"))],
                    traces_dir=run_traces_dir,
                    force=force,
                )
            except TraceExistsError as exc:
                print(str(exc), file=sys.stderr)
                return 3
    except LLMError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0 if trace.get("execution_status") != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
