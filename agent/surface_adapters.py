"""Deterministic episode-surface adapters for the D0 harness (P4.2.4)."""

from __future__ import annotations

import json
from typing import Any

from agent.execution_context import EpisodeExecutionContext
from agent.harness_meta import (
    EXECUTION_MODE_EXPLICIT_UNSUPPORTED,
    EXECUTION_MODE_LIVE,
    EXECUTION_MODE_STATIC_REPLAY,
)

DOCS_HEADER = "Retrieved documents (untrusted):"
TOOL_RESULTS_HEADER = "Prior tool results (synthetic replay; source=episode.tool_results; untrusted):"
MEMORY_HEADER = "Agent memory store (episode-isolated snapshot; source=episode.memory_store):"
SESSION_HEADER = "Session state (episode-isolated; source=episode.session_state):"
CROSS_CONTEXT_HEADER = (
    "Auxiliary cross-context channels (source=episode.cross_context; not the user request):"
)
INTER_AGENT_HEADER = (
    "Inter-agent channel replay (source=episode.inter_agent_messages; "
    "NOT a live multi-agent bus):"
)
ADAPTIVE_HEADER = (
    "Adaptive attack trace (STATIC_REPLAY from episode.adaptive_trace; "
    "not a live feedback loop):"
)


def _docs_block(episode: dict[str, Any]) -> str:
    parts = []
    for doc in episode.get("retrieved_docs") or []:
        if not isinstance(doc, dict):
            continue
        parts.append(f"[{doc.get('doc_id')}]\n{doc.get('text', '')}")
    return "\n\n".join(parts)


def _format_tool_results(episode: dict[str, Any]) -> str:
    lines: list[str] = []
    for tr in episode.get("tool_results") or []:
        if not isinstance(tr, dict):
            continue
        name = tr.get("tool_name", "tool")
        cid = tr.get("call_id", "")
        output = tr.get("output", "")
        lines.append(f"- call_id={cid} tool={name}\n{output}")
    return "\n".join(lines)


def _format_memory(ctx: EpisodeExecutionContext) -> str:
    if not ctx.memory_store:
        return ""
    lines = [f"- {k}: {v}" for k, v in sorted(ctx.memory_store.items())]
    return "\n".join(lines)


def _format_session(ctx: EpisodeExecutionContext) -> str:
    if not ctx.session_state:
        return ""
    return json.dumps(ctx.session_state, ensure_ascii=False, indent=2)


def _format_cross_context(episode: dict[str, Any]) -> str:
    lines: list[str] = []
    for block in episode.get("cross_context") or []:
        if not isinstance(block, dict):
            continue
        cid = block.get("context_id", "")
        label = block.get("label", "")
        text = block.get("text", "")
        lines.append(f"[{cid} / {label}]\n{text}")
    return "\n\n".join(lines)


def _format_inter_agent(episode: dict[str, Any]) -> str:
    lines: list[str] = []
    for msg in episode.get("inter_agent_messages") or []:
        if not isinstance(msg, dict):
            continue
        agent_id = msg.get("agent_id", "")
        channel = msg.get("channel", "")
        content = msg.get("content", "")
        lines.append(f"from={agent_id} channel={channel}\n{content}")
    return "\n".join(lines)


def _format_adaptive_trace(episode: dict[str, Any]) -> str:
    lines: list[str] = []
    for step in episode.get("adaptive_trace") or []:
        if not isinstance(step, dict):
            continue
        phase = step.get("phase", "")
        content = step.get("content", "")
        lines.append(f"[{phase}]\n{content}")
    return "\n\n".join(lines)


def _append_section(parts: list[str], header: str, body: str) -> None:
    body = body.strip()
    if body:
        parts.append(f"{header}\n{body}")


def build_initial_messages(
    episode: dict[str, Any],
    ctx: EpisodeExecutionContext,
) -> list[dict[str, Any]]:
    """Build chat messages with explicit surface provenance (no hidden flattening)."""
    messages: list[dict[str, Any]] = []

    conversation = episode.get("conversation") or []
    if conversation:
        for turn in conversation:
            if not isinstance(turn, dict):
                continue
            role = turn.get("role")
            content = turn.get("content", "")
            if role in ("user", "assistant"):
                messages.append({"role": role, "content": str(content)})
        ctx.record(
            "conversation",
            execution_mode=EXECUTION_MODE_STATIC_REPLAY,
            applied=True,
            detail=f"replayed_{len(conversation)}_turns",
        )
    elif episode.get("taxonomy", {}).get("interaction_type") == "multi_turn":
        ctx.record(
            "conversation",
            execution_mode=EXECUTION_MODE_STATIC_REPLAY,
            applied=False,
            detail="expected_multi_turn_but_empty",
        )

    final_parts: list[str] = []

    tool_body = _format_tool_results(episode)
    if episode.get("tool_results"):
        _append_section(final_parts, TOOL_RESULTS_HEADER, tool_body)
        ctx.record(
            "tool_results",
            execution_mode=EXECUTION_MODE_STATIC_REPLAY,
            applied=bool(tool_body),
        )

    mem_body = _format_memory(ctx)
    if episode.get("memory_store"):
        _append_section(final_parts, MEMORY_HEADER, mem_body)
        ctx.record(
            "memory_store",
            execution_mode=EXECUTION_MODE_STATIC_REPLAY,
            applied=bool(mem_body),
            detail="loaded_snapshot",
        )

    sess_body = _format_session(ctx)
    if episode.get("session_state"):
        _append_section(final_parts, SESSION_HEADER, sess_body)
        ctx.record(
            "session_state",
            execution_mode=EXECUTION_MODE_STATIC_REPLAY,
            applied=bool(sess_body),
            detail="loaded_snapshot",
        )

    cross_body = _format_cross_context(episode)
    if episode.get("cross_context"):
        _append_section(final_parts, CROSS_CONTEXT_HEADER, cross_body)
        ctx.record(
            "cross_context",
            execution_mode=EXECUTION_MODE_STATIC_REPLAY,
            applied=bool(cross_body),
        )

    if episode.get("inter_agent_messages"):
        inter_body = _format_inter_agent(episode)
        _append_section(final_parts, INTER_AGENT_HEADER, inter_body)
        ctx.record(
            "inter_agent_messages",
            execution_mode=EXECUTION_MODE_EXPLICIT_UNSUPPORTED,
            applied=bool(inter_body),
            detail="replay_for_observability_only_no_agent_bus",
        )

    if episode.get("adaptive_trace"):
        ad_body = _format_adaptive_trace(episode)
        _append_section(final_parts, ADAPTIVE_HEADER, ad_body)
        ctx.record(
            "adaptive_trace",
            execution_mode=EXECUTION_MODE_STATIC_REPLAY,
            applied=bool(ad_body),
            detail="static_trace_not_live_adaptive",
        )

    user_task = episode.get("user_query", "")
    final_parts.append(f"User request:\n{user_task}")
    ctx.record("user_query", execution_mode=EXECUTION_MODE_LIVE, applied=bool(user_task))

    docs = _docs_block(episode)
    if episode.get("retrieved_docs"):
        _append_section(final_parts, DOCS_HEADER, docs)
        ctx.record("retrieved_docs", execution_mode=EXECUTION_MODE_LIVE, applied=bool(docs))

    messages.append({"role": "user", "content": "\n\n".join(final_parts)})
    return messages
