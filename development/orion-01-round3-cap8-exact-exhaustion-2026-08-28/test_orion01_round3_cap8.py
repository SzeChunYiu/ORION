from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parent
MODULE = HERE / "run_orion01_round3_cap8.py"
spec = importlib.util.spec_from_file_location("orion01_r3_cap8", MODULE)
assert spec is not None and spec.loader is not None
r3 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r3
spec.loader.exec_module(r3)


def test_frozen_task_identity_and_budget() -> None:
    assert r3.STATE_CAP == 500_000
    assert r3.TASKS == (
        (259, ("S0", "CX10", "S0")),
        (261, ("S0", "CX10", "T0")),
        (316, ("S1", "CX01", "S1")),
        (318, ("S1", "CX01", "T1")),
        (387, ("T0", "CX10", "S0")),
        (389, ("T0", "CX10", "T0")),
        (444, ("T1", "CX01", "S1")),
        (446, ("T1", "CX01", "T1")),
    )


def test_cap_row_remains_fail_closed() -> None:
    payload = r3.build_receipt(0, {"cap_hit": True, "word_index": 259, "word": ["S0", "CX10", "S0"]})
    assert payload["terminal"] == "CANNOT_CHECK_MOVE_COMPLETENESS"
    assert payload["scientific_authority_delta"] == "NONE"
    assert payload["approximate_result_promoted"] is False


def test_exhausted_row_gets_only_task_level_terminal() -> None:
    row = {"cap_hit": False, "word_index": 259, "word": ["S0", "CX10", "S0"], "strict_gap": False}
    payload = r3.build_receipt(0, row)
    assert payload["terminal"] == "R3_CAP8_TASK_EXACT_EXHAUSTION_COMPLETE"
    assert payload["full_domain_terminal_claimed"] is False


def test_task_index_rejected() -> None:
    with pytest.raises(ValueError, match="task index"):
        r3.task_at(8)


def test_task_set_terminal_is_fail_closed() -> None:
    payloads = [{"task_index": i, "terminal": "R3_CAP8_TASK_EXACT_EXHAUSTION_COMPLETE"} for i in range(8)]
    payloads[3]["terminal"] = "CANNOT_CHECK_MOVE_COMPLETENESS"
    assert r3.task_set_terminal(payloads) == "CANNOT_CHECK_MOVE_COMPLETENESS"


def test_task_set_terminal_requires_all_exact_tasks() -> None:
    payloads = [{"task_index": i, "terminal": "R3_CAP8_TASK_EXACT_EXHAUSTION_COMPLETE"} for i in range(8)]
    assert r3.task_set_terminal(payloads) == "R3_CAP8_TASK_SET_EXACT_EXHAUSTION_COMPLETE"
    with pytest.raises(ValueError, match="exact task set"):
        r3.task_set_terminal(payloads[:-1])
