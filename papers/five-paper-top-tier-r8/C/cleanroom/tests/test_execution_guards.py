from __future__ import annotations

import json
from pathlib import Path

import pytest

import build_manifest
import fiberguard_cleanroom as fg
import run_replay
import verify_receipt


def _manifest(tmp_path: Path) -> dict[str, object]:
    (tmp_path / "source.py").write_text("value = 1\n")
    return fg.build_manifest(tmp_path, ("source.py",))


def test_fixture_receipt_is_sealed_without_packet_or_panel_outcomes(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    receipt = run_replay.prepare_fixture_receipt(manifest)
    assert fg.verify_sealed_payload(receipt)
    assert receipt["binding"]["manifest_sha256"] == manifest["manifest_sha256"]
    assert receipt["payload"]["full_panel_execution"] == "NOT_RUN"
    assert receipt["payload"]["independence_terminal"] == "CANNOT_CHECK"
    assert receipt["payload"]["blinding_breach"] == "BLINDING_BREACH_ISSUE_BODY"


def test_execute_mode_checks_packet_before_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = _manifest(tmp_path)
    packet_path = tmp_path / "R8_PACKET_COMMIT.json"
    packet_path.write_text(
        json.dumps(
            {
                "schema": "ORION.FivePaperR8.PacketCommit.v1",
                "packet_commit": "TO_BE_BOUND_AFTER_MATERIALIZATION",
                "base_commit": "0" * 40,
                "branch": "codex/five-paper-top-tier-r8-20260826",
            }
        )
    )
    dispatched = False

    def forbidden_dispatch(*, workers: int) -> dict[str, object]:
        nonlocal dispatched
        dispatched = True
        return {"workers": workers}

    monkeypatch.setattr(run_replay.fg, "execute_all_panels", forbidden_dispatch)
    with pytest.raises(fg.PacketIdentityUnresolved, match="placeholder"):
        run_replay.prepare_execution_receipt(
            manifest=manifest,
            packet_path=packet_path,
            repository=tmp_path,
            workers=16,
        )
    assert not dispatched


def test_receipt_verifier_binds_manifest_and_rejects_tamper(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    receipt = run_replay.prepare_fixture_receipt(manifest)
    verify_receipt.verify_receipt(root=tmp_path, manifest=manifest, receipt=receipt)

    receipt["binding"]["manifest_sha256"] = "f" * 64
    with pytest.raises(verify_receipt.ReceiptMismatch, match="manifest"):
        verify_receipt.verify_receipt(root=tmp_path, manifest=manifest, receipt=receipt)


def test_atomic_json_writer_leaves_no_partial_file(tmp_path: Path) -> None:
    destination = tmp_path / "receipt.json"
    run_replay.write_json_atomic(destination, {"b": 2, "a": 1})
    assert destination.read_text() == '{\n  "a": 1,\n  "b": 2\n}\n'
    assert list(tmp_path.glob("*.tmp")) == []


def test_source_manifest_allowlist_is_cleanroom_local_and_unique() -> None:
    paths = build_manifest.SOURCE_PATHS
    assert len(paths) == len(set(paths))
    assert paths == tuple(sorted(paths))
    assert "fiberguard_cleanroom.py" in paths
    assert "tests/test_fiberguard_cleanroom.py" in paths
    assert all(not path.startswith("../") and "/artifact/" not in f"/{path}" for path in paths)


def test_slurm_envelope_and_packet_gate_are_static() -> None:
    script = (
        Path(__file__).resolve().parents[1] / "slurm" / "job_c_r8_1.slurm"
    ).read_text()
    assert "#SBATCH --cpus-per-task=16" in script
    assert "#SBATCH --mem=32G" in script
    assert "#SBATCH --time=02:00:00" in script
    assert "--mode execute" in script
    assert "R8_PACKET_COMMIT.json" in script
    assert "--workers 16" in script


@pytest.mark.parametrize(
    "sample",
    (0, 1, 7, 1_234, 23_456, 2**15 - 1),
)
def test_graph_sample_has_three_way_target_agreement(sample: int) -> None:
    first = fg.graph_chromatic_by_coloring(sample)
    second = fg.graph_chromatic_by_independent_cover(sample)
    third = fg.graph_endpoint_check(sample)["target"]
    assert first == second == third


def test_cover_and_cnf_samples_have_three_way_target_agreement() -> None:
    cover_samples = fg.cover_families()[::25_000]
    for family in cover_samples:
        assert (
            fg.cover_size_by_subset_search(family)
            == fg.cover_size_by_mask_dp(family)
            == fg.cover_endpoint_check(family)["target"]
        )

    cnf_samples = fg.cnf_formulas()[::7_000]
    for formula in cnf_samples:
        assert (
            fg.cnf_count_by_truth_table(formula)
            == fg.cnf_count_by_clause_recursion(formula)
            == fg.cnf_endpoint_check(formula)["target"]
        )
