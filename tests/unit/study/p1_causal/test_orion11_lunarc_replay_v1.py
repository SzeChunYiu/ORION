from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

import pytest


DRIVER = (
    Path(__file__).resolve().parents[4]
    / "papers/orion-11-recursive-epistemic-reconstruction/revival"
    / "r1-negative-revival-audit/lunarc-replay-v1"
    / "run_orion11_lunarc_replay_v1.py"
)


def _load_driver():
    assert DRIVER.is_file(), "the frozen ORION-11 replay driver must exist"
    spec = importlib.util.spec_from_file_location("orion11_lunarc_replay_v1", DRIVER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _lane_fixture(repo_root: Path) -> tuple[dict[str, object], bytes, bytes, bytes]:
    public = b'{"task_id":"p-1"}\n'
    protected = b'{"task_id":"p-1","answer":true}\n'
    freeze = b'{"schema_version":"fixture.world-freeze.v1"}\n'
    inputs = repo_root / "inputs"
    inputs.mkdir()
    for name, payload in (
        ("WORLD_PUBLIC.jsonl.gz", public),
        ("PROTECTED_RESPONSE_MATRIX.jsonl.gz", protected),
    ):
        (inputs / name).write_bytes(gzip.compress(payload, mtime=0))
    (inputs / "WORLD_FREEZE.json").write_bytes(freeze)
    lane = {
        "name": "fixture",
        "inputs": {
            "world_public_gzip": {
                "path": "inputs/WORLD_PUBLIC.jsonl.gz",
                "sha256": _sha256((inputs / "WORLD_PUBLIC.jsonl.gz").read_bytes()),
                "decompressed_sha256": _sha256(public),
            },
            "protected_response_matrix_gzip": {
                "path": "inputs/PROTECTED_RESPONSE_MATRIX.jsonl.gz",
                "sha256": _sha256((inputs / "PROTECTED_RESPONSE_MATRIX.jsonl.gz").read_bytes()),
                "decompressed_sha256": _sha256(protected),
            },
            "world_freeze": {
                "path": "inputs/WORLD_FREEZE.json",
                "sha256": _sha256(freeze),
            },
        },
    }
    return lane, public, protected, freeze


def test_materialize_world_reconstructs_all_bound_inputs(tmp_path: Path) -> None:
    driver = _load_driver()
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    lane, public, protected, freeze = _lane_fixture(repo_root)

    receipt = driver.materialize_world(repo_root, lane, tmp_path / "world")

    assert (tmp_path / "world/WORLD_PUBLIC.jsonl").read_bytes() == public
    assert (tmp_path / "world/PROTECTED_RESPONSE_MATRIX.jsonl").read_bytes() == protected
    assert (tmp_path / "world/WORLD_FREEZE.json").read_bytes() == freeze
    assert receipt["all_input_bindings_pass"] is True


def test_materialize_world_rejects_compressed_archive_drift(tmp_path: Path) -> None:
    driver = _load_driver()
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    lane, _, _, _ = _lane_fixture(repo_root)
    lane["inputs"]["world_public_gzip"]["sha256"] = "0" * 64

    with pytest.raises(driver.ReplayError, match="digest mismatch"):
        driver.materialize_world(repo_root, lane, tmp_path / "world")


def test_compare_exact_reports_byte_identity_and_drift(tmp_path: Path) -> None:
    driver = _load_driver()
    expected = tmp_path / "expected.json"
    actual = tmp_path / "actual.json"
    expected.write_bytes(b'{"x":1}\n')
    actual.write_bytes(expected.read_bytes())

    identical = driver.compare_exact(actual, expected)
    assert identical["byte_equal"] is True
    assert identical["terminal"] == "BYTE_IDENTICAL"
    assert identical["actual_sha256"] == identical["expected_sha256"]

    actual.write_bytes(b'{"x":2}\n')
    drift = driver.compare_exact(actual, expected)
    assert drift["byte_equal"] is False
    assert drift["terminal"] == "BYTE_DIFFERENT__PRESERVE_DISCREPANCY"


def test_load_protocol_rejects_duplicate_lane_names(tmp_path: Path) -> None:
    driver = _load_driver()
    protocol = tmp_path / "protocol.json"
    protocol.write_text(
        json.dumps(
            {
                "schema_version": "orion.orion11.lunarc-replay-protocol.v1",
                "replay_id": "fixture",
                "lanes": [{"name": "primary"}, {"name": "primary"}],
            }
        )
    )

    with pytest.raises(driver.ReplayError, match="duplicate lane"):
        driver.load_protocol(protocol)


def test_output_summary_reads_the_result_terminal(tmp_path: Path) -> None:
    driver = _load_driver()
    result = tmp_path / "RESULT.json"
    verification = tmp_path / "INDEPENDENT_VERIFICATION.json"
    result.write_text(json.dumps({"terminal": "P1_MUTATION_NECESSITY_SUPPORTED"}))
    verification.write_text(
        json.dumps(
            {
                "verdict": "PASS",
                "score_mismatch_count": 0,
                "analysis_mismatch_count": 0,
            }
        )
    )

    summary = driver.output_summary(result, verification)

    assert summary["scientific_terminal"] == "P1_MUTATION_NECESSITY_SUPPORTED"
    assert summary["independent_verdict"] == "PASS"


def test_run_command_preserves_nonzero_exit_as_a_receipt(tmp_path: Path) -> None:
    driver = _load_driver()
    stdout = tmp_path / "stdout.log"
    stderr = tmp_path / "stderr.log"

    receipt = driver._run_command(
        [sys.executable, "-c", "import sys; print('adverse', file=sys.stderr); sys.exit(7)"],
        cwd=tmp_path,
        env=os.environ.copy(),
        stdout_path=stdout,
        stderr_path=stderr,
    )

    assert receipt["completed"] is False
    assert receipt["returncode"] == 7
    assert stderr.read_text().strip() == "adverse"
