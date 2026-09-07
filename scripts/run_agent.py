#!/usr/bin/env python3
"""Run one episode through the Phase 2 LLM harness and write an auditable trace.

Uses only mock tools (search_docs, send_email). D0 undefended prompt by default.
No defenses. Does not score ASR or utility. Configure via .env.example.

Examples:
  python scripts/run_agent.py --dry-run --episode examples/episode_attack_001.json
  python scripts/run_agent.py --id atk_002
  python scripts/run_agent.py --smoke   # 1 attack + 1 benign if an API key is set
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
from agent.load import load_episode, load_episode_by_id  # noqa: E402
from agent.loop import DEFAULT_PROMPT_ID, run_episode  # noqa: E402
from agent.traces import (  # noqa: E402
    RESULTS_TRACES_DIR,
    default_trace_path,
    make_run_id,
    write_manifest,
    write_trace,
)


def _print_trace(trace: dict) -> None:
    print(json.dumps({k: v for k, v in trace.items() if not str(k).startswith("_")}, indent=2))


def _run_one(
    episode: dict,
    *,
    dry_run: bool,
    out_dir: Path,
    no_write: bool,
    max_steps: int | None,
    run_id: str | None = None,
    prompt_id: str = DEFAULT_PROMPT_ID,
) -> dict:
    if dry_run:
        trace = run_episode(
            episode,
            dry_run=True,
            max_steps=max_steps,
            run_id=run_id,
            prompt_id=prompt_id,
        )
    else:
        try:
            config = config_from_env(require_key=True)
        except LLMConfigError as exc:
            print(str(exc), file=sys.stderr)
            raise SystemExit(2) from exc
        if max_steps is not None:
            config = replace(config, max_steps=max_steps)
        client = OpenAICompatibleClient(config)
        if run_id is None:
            run_id = make_run_id(
                model=config.model, episode_id=str(episode.get("id") or "unknown")
            )
        trace = run_episode(
            episode,
            client=client,
            config=config,
            max_steps=max_steps,
            run_id=run_id,
            prompt_id=prompt_id,
        )
    _print_trace(trace)
    if no_write:
        return trace
    episode_id = str(trace.get("episode_id") or episode.get("id") or "unknown")
    path = default_trace_path(episode_id, out_dir)
    write_trace(trace, path)
    print(f"wrote {path}", file=sys.stderr)
    return trace


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--episode",
        type=Path,
        default=None,
        help="Path to one episode JSON.",
    )
    parser.add_argument(
        "--id",
        dest="episode_id",
        default=None,
        help="Load episode by id from data/episodes/ or examples/.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=RESULTS_TRACES_DIR,
        help="Trace directory (default: results/traces/).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write this run's trace to an explicit path (single episode only).",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print the trace JSON but do not write a file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not call an LLM. Emit a dry_run trace (not an evaluation).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Bound the tool loop (default: AIB_LLM_MAX_STEPS or 6).",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Pipeline check only: run atk_002 and ben_002. Not an evaluation.",
    )
    parser.add_argument(
        "--prompt-id",
        default=DEFAULT_PROMPT_ID,
        help="Prompt condition id (default: d0 = undefended baseline).",
    )
    args = parser.parse_args()

    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    prompt_id = args.prompt_id

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
                path = default_trace_path(str(trace.get("episode_id") or episode_id), out_dir)
                write_trace(trace, path)
                print(f"wrote {path}", file=sys.stderr)
            traces.append(trace)
        statuses = [str(t.get("execution_status")) for t in traces]
        if not args.no_write:
            manifest_path = write_manifest(
                batch_run_id,
                episode_ids=["atk_002", "ben_002"],
                model=config.model,
                temperature=config.temperature,
                seed=config.seed,
                prompt_id=prompt_id,
                defense_condition="d0" if prompt_id == "d0" else prompt_id,
                statuses=statuses,
                traces_dir=str(out_dir),
                note="Smoke pipeline only. Not ASR/utility.",
            )
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
        if args.out and not args.no_write:
            if args.dry_run:
                trace = run_episode(
                    episode, dry_run=True, max_steps=args.max_steps, prompt_id=prompt_id
                )
            else:
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
                write_manifest(
                    run_id,
                    episode_ids=[str(episode.get("id") or "")],
                    model=config.model,
                    temperature=config.temperature,
                    seed=config.seed,
                    prompt_id=prompt_id,
                    defense_condition="d0" if prompt_id == "d0" else prompt_id,
                    statuses=[str(trace.get("execution_status"))],
                    traces_dir=str(Path(args.out).parent),
                )
            _print_trace(trace)
            out_path = args.out if args.out.is_absolute() else ROOT / args.out
            write_trace(trace, out_path)
            print(f"wrote {out_path}", file=sys.stderr)
            return 0 if trace.get("execution_status") != "error" else 1
        trace = _run_one(
            episode,
            dry_run=args.dry_run,
            out_dir=out_dir,
            no_write=args.no_write,
            max_steps=args.max_steps,
            prompt_id=prompt_id,
        )
        if not args.dry_run and not args.no_write and trace.get("run_id"):
            write_manifest(
                str(trace["run_id"]),
                episode_ids=[str(trace.get("episode_id") or "")],
                model=str(trace.get("model") or ""),
                temperature=trace.get("temperature"),
                seed=trace.get("seed"),
                prompt_id=str(trace.get("prompt_id") or prompt_id),
                defense_condition=str(trace.get("defense_condition") or "d0"),
                statuses=[str(trace.get("execution_status"))],
                traces_dir=str(out_dir),
            )
    except LLMError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0 if trace.get("execution_status") != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
