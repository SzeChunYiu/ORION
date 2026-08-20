from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


def test_p10_cost_table_sentinel_is_representable():
    repo_root = Path(__file__).resolve().parents[3]
    script = repo_root / "research/extensions/orion-q/max_r6_p10_candidate_blind_frame_optimizer.py"
    text = script.read_text()
    assert "INF = 10**9" in text
    assert "LOCAL = np.full((4, 4, 4, 3, 32), INF, dtype=np.int32)" in text
    assert np.iinfo(np.int32).max >= 10**9
