from __future__ import annotations

from pathlib import Path

import pytest

np = pytest.importorskip(
    "numpy", reason="ORION-Q numeric regressions need the optional orion-q extra"
)


def test_p10_cost_table_and_accumulators_cover_full_subject_depth():
    repo_root = Path(__file__).resolve().parents[3]
    script = repo_root / "research/extensions/orion-q/max_r6_p10_candidate_blind_frame_optimizer.py"
    text = script.read_text()

    assert "INF = 10**9" in text
    assert "dp = np.full(8, INF, dtype=np.int64)" in text
    assert "local = np.full(8, INF, dtype=np.int64)" in text
    assert "LOCAL = np.full((4, 4, 4, 3, 32), INF, dtype=np.int64)" in text
    assert "dp = np.full(32, INF, dtype=np.int64)" in text
    assert ".astype(np.int64)" in text

    # The frozen subjects reach 12 qubits. Unreachable-state sentinels can be
    # accumulated once per qubit before minimization, so represent n*INF, not
    # merely INF itself. This is the regression that the earlier int32 guard missed.
    max_subject_qubits = 12
    required = max_subject_qubits * 10**9
    assert np.iinfo(np.int32).max < required
    assert np.iinfo(np.int64).max > required
