"""External AdaptiGuard D2 bridge for agent-injection-bench (runtime + offline tests)."""

from d2_bridge.config import (
    ADAPTI_GUARD_COMMIT_PIN,
    D2_BRIDGE_VERSION,
    D2DefenseConfig,
    DEFAULT_DENY_MESSAGE_MODE,
)
from d2_bridge.loop import run_d2_episode

__all__ = [
    "ADAPTI_GUARD_COMMIT_PIN",
    "D2_BRIDGE_VERSION",
    "D2DefenseConfig",
    "DEFAULT_DENY_MESSAGE_MODE",
    "run_d2_episode",
]
