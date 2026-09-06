from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def root() -> Path:
    return ROOT


@pytest.fixture
def attack_example() -> Path:
    return ROOT / "examples" / "episode_attack_001.json"


@pytest.fixture
def benign_example() -> Path:
    return ROOT / "examples" / "episode_benign_001.json"


@pytest.fixture
def attack_seed() -> Path:
    return ROOT / "data" / "episodes" / "attack" / "atk_002.json"
