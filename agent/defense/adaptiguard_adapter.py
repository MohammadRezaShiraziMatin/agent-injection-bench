"""Map AIB episodes/messages to real AdaptiGuard CoreDefensePipeline (no guessed API)."""

from __future__ import annotations

from typing import Any

from agent.defense.types import DefenseAction


def episode_input_from_aib(
    episode: dict[str, Any],
    messages: list[dict[str, Any]],
) -> Any:
    from adapti_guard.core.episode import EpisodeInput

    docs = episode.get("retrieved_docs") or []
    context_parts: list[str] = []
    for doc in docs:
        if isinstance(doc, dict):
            title = doc.get("title") or doc.get("id") or "doc"
            body = doc.get("content") or doc.get("text") or ""
            context_parts.append(f"[{title}]\n{body}")
        else:
            context_parts.append(str(doc))
    context = "\n\n".join(context_parts)
    prompt = str(episode.get("user_query") or "")
    if not prompt:
        for msg in messages:
            if msg.get("role") == "user" and msg.get("content"):
                prompt = str(msg["content"])
                break
    return EpisodeInput(prompt=prompt, context=context)


def _map_policy_action(policy_action: str, trace: Any) -> str:
    from adapti_guard.core.models import DefenseAction as AgDefenseAction

    if trace.blocked or policy_action == AgDefenseAction.BLOCK.value:
        return DefenseAction.BLOCK.value
    if policy_action == AgDefenseAction.SANITIZE.value:
        return DefenseAction.TRANSFORM.value
    if policy_action == AgDefenseAction.TOOL_RESTRICTION.value:
        return DefenseAction.DETECT_ONLY.value
    if policy_action == AgDefenseAction.NO_INTERVENTION.value:
        return DefenseAction.ALLOW.value
    return DefenseAction.ALLOW.value


def _apply_content_to_messages(
    messages: list[dict[str, Any]],
    content: str,
    *,
    transform: bool,
) -> list[dict[str, Any]]:
    if not transform or not content:
        return messages
    out: list[dict[str, Any]] = []
    replaced = False
    for msg in messages:
        m = dict(msg)
        if not replaced and m.get("role") == "user":
            m["content"] = content
            replaced = True
        out.append(m)
    return out


def run_core_pipeline(
    *,
    episode: dict[str, Any],
    messages: list[dict[str, Any]],
    dry_run: bool,
    pipeline: Any | None = None,
) -> dict[str, Any]:
    """Invoke AdaptiGuard CoreDefensePipeline; return AIB bridge dict."""
    from adapti_guard.core.core_pipeline import CoreDefensePipeline

    pipe = pipeline or CoreDefensePipeline()
    inp = episode_input_from_aib(episode, messages)
    trace = pipe.run(inp)
    decision = _map_policy_action(trace.policy_action, trace)
    block = decision == DefenseAction.BLOCK.value
    transform = decision == DefenseAction.TRANSFORM.value
    new_messages = _apply_content_to_messages(
        messages,
        trace.content if transform else "",
        transform=transform,
    )
    skip_target = block
    target_reached = not skip_target
    return {
        "decision": decision,
        "reason": trace.policy_reason or trace.tool_reason,
        "category": trace.policy_action,
        "detector_invoked": True,
        "detector_result": "hit" if trace.detector_hit else "no_hit",
        "risk_score": trace.risk_score,
        "risk_level": trace.risk_level,
        "target_reached": target_reached,
        "skip_target_model": skip_target,
        "messages": new_messages,
        "synthetic_final_answer": "[defense-blocked]" if block else None,
        "defense_error": False,
        "dry_run": dry_run,
        "adaptiguard_trace": trace.to_dict(),
        "tool_access": trace.tool_access,
    }
