from __future__ import annotations

from agent.adaptive_runtime import run_live_adaptive_loop, run_static_adaptive_replay
from agent.harness_meta import (
    EXECUTION_MODE_LIVE_ADAPTIVE,
    EXECUTION_MODE_STATIC_ADAPTIVE_REPLAY,
)


def test_static_adaptive_replay_mode():
    ep = {
        "adaptive_trace": [
            {"phase": "attack", "content": "a1"},
            {"phase": "observe", "content": "o1"},
        ]
    }
    out = run_static_adaptive_replay(ep)
    assert out["execution_mode"] == EXECUTION_MODE_STATIC_ADAPTIVE_REPLAY
    assert out["rounds"] == 2


def test_live_adaptive_bounded_deterministic():
    def observer(attack: str) -> str:
        return f"echo:{attack[:20]}"

    out = run_live_adaptive_loop(
        seed=43020260921,
        max_rounds=3,
        initial_attack="start",
        observer=observer,
    )
    assert out["execution_mode"] == EXECUTION_MODE_LIVE_ADAPTIVE
    assert 1 <= out["rounds_executed"] <= 3
    assert out["trace"][0]["attack"] == "start"
