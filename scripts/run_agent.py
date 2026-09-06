#!/usr/bin/env python3
"""Load an episode, bind mock RAG + email tools, and (by default) dry-run.

This is an interface stub. It does not call a hosted LLM and does not
implement a defense. Use it to inspect an episode and emit a dry-run
trace that scoring scripts can read.

Trace shape (one JSON object per file):
{
  "episode_id": "atk_001",
  "split": "attack",
  "tool_calls": [{"name": "search_docs", "arguments": {"query": "..."}}],
  "final_answer": "...",
  "dry_run": true
}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts._common import TRACES_DIR, dump_json, load_json  # noqa: E402
from tools.mock_search_docs import search_docs  # noqa: E402
from tools.mock_send_email import reset_log, send_email  # noqa: E402


def _bind_search(retrieved_docs: list[dict]):
    def _search(query: str) -> list[str]:
        return search_docs(query, retrieved_docs=retrieved_docs)

    return _search


def _describe_tools() -> list[dict]:
    return [
        {
            "name": "search_docs",
            "signature": "search_docs(query: str) -> list[str]",
            "description": "Return texts from the episode's retrieved_docs. No network.",
        },
        {
            "name": "send_email",
            "signature": "send_email(to: str, subject: str, body: str) -> dict",
            "description": "Log an email call. v0 misuse target. No network.",
        },
    ]


def run_episode(episode: dict, *, dry_run: bool) -> dict:
    reset_log()
    retrieved = episode.get("retrieved_docs") or []
    bound_search = _bind_search(retrieved)

    print("=== episode ===")
    print(f"id:    {episode.get('id')}")
    print(f"split: {episode.get('split')}")
    print(f"query: {episode.get('user_query')}")
    print(f"docs:  {len(retrieved)}")
    print("=== tools ===")
    for tool in _describe_tools():
        print(f"- {tool['signature']}")

    # Demonstrate the bound search callable (does not count as an agent tool call).
    preview = bound_search(str(episode.get("user_query") or ""))
    print(f"=== mock_search_docs preview ({len(preview)} hit(s)) ===")
    for i, text in enumerate(preview, start=1):
        snippet = text.replace("\n", " ")
        print(f"[{i}] {snippet[:160]}{'…' if len(snippet) > 160 else ''}")

    if not dry_run:
        print(
            "No LLM backend is wired in v0. Refusing to invent tool calls.\n"
            "Re-run without --execute, or implement an agent loop that calls "
            "search_docs / send_email and writes a real trace.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    trace = {
        "episode_id": episode.get("id"),
        "split": episode.get("split"),
        "tool_calls": [],
        "final_answer": (
            "dry-run stub: no LLM was called; no tool_calls were issued. "
            "This is not an evaluation result."
        ),
        "dry_run": True,
    }
    # Keep send_email imported so the interface is obvious to readers / IDEs.
    _ = send_email
    return trace


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--episode",
        type=Path,
        default=ROOT / "examples" / "episode_attack_001.json",
        help="Path to one episode JSON (default: examples/episode_attack_001.json)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write the dry-run trace JSON here (optional).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=TRACES_DIR,
        help="If --out is omitted, write <out-dir>/<episode_id>.dry_run.json",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Reserved. v0 has no LLM backend; this flag exits with status 2.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print the trace JSON but do not write a file.",
    )
    args = parser.parse_args()

    episode_path = args.episode if args.episode.is_absolute() else ROOT / args.episode
    episode = load_json(episode_path)
    if not isinstance(episode, dict):
        print("Episode root must be a JSON object.", file=sys.stderr)
        return 1

    trace = run_episode(episode, dry_run=not args.execute)
    print("=== dry-run trace ===")
    printable = {k: v for k, v in trace.items() if k != "final_answer"}
    printable["final_answer"] = trace["final_answer"]
    print(json.dumps(printable, indent=2))

    if args.no_write:
        return 0

    out_path = args.out
    if out_path is None:
        episode_id = str(episode.get("id") or "unknown")
        out_path = args.out_dir / f"{episode_id}.dry_run.json"
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    dump_json(out_path, trace)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
