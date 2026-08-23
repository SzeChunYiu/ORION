from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / "papers/candidates/checkers/check_reproducibility_targets_v2.py"


def _checker():
    spec = importlib.util.spec_from_file_location("check_reproducibility_targets_v2", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_subject(tmp_path: Path, candidate_id: str) -> Path:
    checker = _checker()
    root = tmp_path / "repo"
    paper = checker.PAPERS[candidate_id]
    shutil.copytree(ROOT / paper, root / paper)
    shutil.copy2(ROOT / "uv.lock", root / "uv.lock")
    return root


EXPECTED_INPUTS = {
    "P6": {
        "papers/paper-06-formal-epistemic-structures-and-mechanics/formal/assumption_countermodels_v2.source.json",
        "papers/paper-06-formal-epistemic-structures-and-mechanics/formal/assumption_countermodels_v2.schema.json",
    },
    "P7": {
        "papers/paper-07-epistemic-navigation-open-worlds/benchmark/instances_v2.schema.json",
    },
    "P8": {
        "papers/paper-08-epistemic-authority-autonomous-science/benchmark/authority_cases_v2.schema.json",
    },
}


@pytest.mark.parametrize("candidate_id", ("P6", "P7", "P8"))
def test_generated_dataset_is_bound_as_output_not_raw_input(candidate_id: str) -> None:
    checker = _checker()
    paper = ROOT / checker.PAPERS[candidate_id]
    contract = json.loads(
        (paper / "evidence/local" / f"{candidate_id}_LOCAL_REPLAY_CONTRACT_V3.json").read_text(
            encoding="utf-8"
        )
    )
    raw_inputs = {entry["path"] for entry in contract["raw_inputs"]}
    raw_outputs = {entry["path"] for entry in contract["raw_outputs"]}
    dataset = (checker.PAPERS[candidate_id] / checker.DATASETS[candidate_id]).as_posix()
    assert raw_inputs == EXPECTED_INPUTS[candidate_id]
    assert dataset not in raw_inputs
    assert dataset in raw_outputs


@pytest.mark.parametrize("candidate_id", ("P6", "P7", "P8"))
def test_malformed_generated_jsonl_cannot_count_as_immutable_output(
    tmp_path: Path, candidate_id: str
) -> None:
    checker = _checker()
    root = _copy_subject(tmp_path, candidate_id)
    paper = root / checker.PAPERS[candidate_id]
    dataset = paper / checker.DATASETS[candidate_id]
    dataset.write_text('{"broken":\n', encoding="utf-8")

    contract_path = paper / "evidence/local" / f"{candidate_id}_LOCAL_REPLAY_CONTRACT_V3.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    relative_dataset = (checker.PAPERS[candidate_id] / checker.DATASETS[candidate_id]).as_posix()
    matched = [entry for entry in contract["raw_outputs"] if entry["path"] == relative_dataset]
    assert len(matched) == 1
    matched[0]["sha256"] = hashlib.sha256(dataset.read_bytes()).hexdigest()
    contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    target = checker._immutable_results(root, candidate_id)
    assert target.status == "PARTIAL"
    assert "local replay contract is malformed" in str(target.blocker)
