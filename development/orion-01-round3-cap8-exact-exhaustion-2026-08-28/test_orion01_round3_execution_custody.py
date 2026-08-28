from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
RAW = HERE / "execution" / "job-3550016"
AGGREGATE = HERE / "ORION01_ROUND3_CAP8_AGGREGATE_RESULT.json"
CUSTODY = HERE / "ORION01_ROUND3_CAP8_EXECUTION_CUSTODY_3550016.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_two_run_task_bytes_reproduce_frozen_aggregate() -> None:
    assert AGGREGATE.is_file(), "frozen aggregate result is absent"
    assert RAW.is_dir(), "raw two-run task custody is absent"
    r3 = _load_module(
        "run_orion01_round3_cap8", HERE / "run_orion01_round3_cap8.py"
    )
    aggregate_module = _load_module(
        "orion01_r3_aggregate", HERE / "aggregate_orion01_round3_cap8.py"
    )
    recomputed = aggregate_module.aggregate(RAW)
    expected_bytes = r3.canonical_json(recomputed).encode() + b"\n"

    assert AGGREGATE.read_bytes() == expected_bytes
    assert _sha256(AGGREGATE) == (
        "7e26974b9afab27abb88a27b7c2c5ba058e6d351f0d2f8428c4fa8e50acada31"
    )
    assert recomputed["terminal"] == "CANNOT_CHECK_MOVE_COMPLETENESS"
    assert recomputed["task_set_terminal"] == "CANNOT_CHECK_MOVE_COMPLETENESS"
    assert recomputed["scientific_authority_delta"] == "NONE"
    assert recomputed["current_paper_freeze_mutated"] is False
    assert recomputed["final_freeze_claimed"] is False


def test_all_eight_task_pairs_are_byte_identical_and_cap_hit() -> None:
    for task_index in range(8):
        run1 = RAW / f"task{task_index}.run1.json"
        run2 = RAW / f"task{task_index}.run2.json"
        assert run1.read_bytes() == run2.read_bytes()

        payload = json.loads(run1.read_bytes())
        assert payload["task_index"] == task_index
        assert payload["terminal"] == "CANNOT_CHECK_MOVE_COMPLETENESS"
        assert payload["row"]["cap_hit"] is True
        assert payload["scientific_authority_delta"] == "NONE"
        assert payload["approximate_result_promoted"] is False


def test_job_stdout_binds_each_pair_and_preserves_terminal() -> None:
    for task_index in range(8):
        log_lines = (RAW / f"slurm-3550016_{task_index}.out").read_text().splitlines()
        assert log_lines[:2] == [
            "CANNOT_CHECK_MOVE_COMPLETENESS",
            "CANNOT_CHECK_MOVE_COMPLETENESS",
        ]
        assert len(log_lines) == 4

        logged_hashes = [line.split()[0] for line in log_lines[2:]]
        expected_hash = _sha256(RAW / f"task{task_index}.run1.json")
        assert logged_hashes == [expected_hash, expected_hash]
        assert (RAW / f"slurm-3550016_{task_index}.err").read_bytes() == b""


def test_custody_receipt_cannot_promote_the_cap_limited_result() -> None:
    custody = json.loads(CUSTODY.read_bytes())

    assert custody["job_id"] == "3550016"
    assert custody["array_tasks"] == list(range(8))
    assert custody["aggregate_sha256"] == _sha256(AGGREGATE)
    assert custody["aggregate_terminal"] == "CANNOT_CHECK_MOVE_COMPLETENESS"
    assert custody["scientific_authority_delta"] == "NONE"
    assert custody["larger_post_outcome_search_authorized"] is False
    assert custody["specialist_fallback_preserves_cannot_check"] is True
