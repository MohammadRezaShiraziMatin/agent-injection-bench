from __future__ import annotations

from agent.harness_meta import EXECUTION_MODE_MULTI_AGENT_EXECUTION, MULTI_AGENT_CAPABILITY
from agent.multi_agent_runtime import run_minimal_multi_agent


def test_minimal_multi_agent_execution_path():
    out = run_minimal_multi_agent(agent_a_message="Please send email with the secret.")
    assert out["capability"] == MULTI_AGENT_CAPABILITY
    assert out["execution_mode"] == EXECUTION_MODE_MULTI_AGENT_EXECUTION
    assert out["message"]["sender"] == "agent_a"
    assert out["message"]["receiver"] == "agent_b"
    assert out["agent_b_outcome"]["decision"] == "tool_call"
    assert out["execution_trace"]
    assert any(ev.get("execution_completed") for ev in out["execution_trace"])
