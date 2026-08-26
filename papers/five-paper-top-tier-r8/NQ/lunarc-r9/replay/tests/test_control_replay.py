from __future__ import annotations

import copy
import sys
from itertools import permutations
from pathlib import Path

import pytest

REPLAY_ROOT = Path(__file__).resolve().parents[1]
ENGINE_B_ROOT = REPLAY_ROOT / "engine_b"
for source_root in (REPLAY_ROOT, ENGINE_B_ROOT):
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))

import control_replay as replay  # noqa: E402
import build_replay_manifest as replay_manifest  # noqa: E402
import engine_b as eb  # noqa: E402
import symmetry  # noqa: E402
import verify_control_receipt as verifier  # noqa: E402


def _linear_map(vector: tuple[int, int, int]) -> tuple[int, int, int]:
    x, y, z = vector
    return ((x + y) % 5, (2 * x + 3 * y) % 5, z)


def test_matrix_action_symmetry_is_independent_and_permutation_invariant() -> None:
    sequence = (
        eb.encode_element((1, 0, 0)),
        eb.encode_element((4, 0, 0)),
        eb.encode_element((0, 1, 0)),
        eb.encode_element((0, 4, 0)),
    )
    transformed = tuple(
        eb.encode_element(_linear_map(eb.decode_element(element))) for element in sequence
    )
    expected = symmetry.canonical_matrix_action(sequence)
    assert symmetry.canonical_matrix_action(transformed) == expected
    for permuted in tuple(permutations(sequence))[:12]:
        assert symmetry.canonical_matrix_action(permuted) == expected
    assert len(symmetry.invertible_matrices(1)) == 4
    assert len(symmetry.invertible_matrices(2)) == 480


def test_crb_source_tree_never_imports_or_calls_engine_a() -> None:
    for path in sorted(ENGINE_B_ROOT.rglob("*.py")):
        source = path.read_text()
        assert "nq_engine_a" not in source
        assert "engine-a-bounded-pilot" not in source


def test_replay_manifest_is_path_scoped_and_tamper_evident() -> None:
    manifest = replay_manifest.build_replay_manifest(REPLAY_ROOT)
    replay_manifest.verify_replay_manifest(REPLAY_ROOT, manifest)
    assert manifest["engine_b_independence"] == "STANDALONE_NO_ENGINE_A_IMPORT"
    assert manifest["full_census_authorized"] is False
    tampered = copy.deepcopy(manifest)
    tampered["files"][0]["sha256"] = "0" * 64
    with pytest.raises(replay_manifest.ReplayManifestMismatch, match="digest"):
        replay_manifest.verify_replay_manifest(REPLAY_ROOT, tampered)


def test_rank_two_control_grammar_is_deterministic_and_has_both_outcomes() -> None:
    cases = replay.frozen_rank_two_cases()
    assert cases == replay.frozen_rank_two_cases()
    assert len(cases) == 61
    assert cases == tuple(sorted(cases, key=lambda value: (len(value), value)))
    assert all(symmetry.span_rank(sequence) == 2 for sequence in cases)
    receipt = replay.build_control_receipt()
    assert receipt["case_count"] == len(cases)
    assert receipt["positive_count"] > 0
    assert receipt["negative_count"] > 0
    assert receipt["mismatch_count"] == 0
    assert receipt["terminal"] == replay.PASS_TERMINAL
    assert receipt["full_census_executed"] is False
    assert receipt["d2_d3_replay_complete"] is False
    assert receipt["science_terminal"] == "CANNOT_CHECK"
    assert receipt["independence_terminal"] == "CANNOT_CHECK"
    verifier.verify_control_receipt(receipt)


def test_two_engine_control_disagreement_emits_bound_witness(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = replay._status_b
    calls = 0

    def disagree_once(
        sequence: tuple[int, ...],
    ) -> tuple[str, list[list[int]] | None, str]:
        nonlocal calls
        calls += 1
        status, witness, digest = original(sequence)
        if calls == 1:
            return ("NEGATIVE" if status == "POSITIVE" else "POSITIVE"), witness, digest
        return status, witness, digest

    monkeypatch.setattr(replay, "_status_b", disagree_once)
    receipt = replay.build_control_receipt()
    assert receipt["terminal"] == replay.DISAGREEMENT_TERMINAL
    assert receipt["mismatch_count"] == 1
    mismatch = receipt["disagreements"][0]
    assert mismatch["record_id"].startswith("rank2-prefix-")
    assert mismatch["sequence"]
    with pytest.raises(verifier.ControlReceiptMismatch, match="PASS terminal"):
        verifier.verify_control_receipt(receipt, rerun=False)


@pytest.mark.parametrize(
    ("field", "replacement", "message"),
    (
        ("terminal", "NQ_D2_D3_INDEPENDENT_REPLAY_PASS", "digest"),
        ("science_terminal", "PASS", "digest"),
        ("full_census_executed", True, "digest"),
    ),
)
def test_control_receipt_rejects_authority_tamper(
    field: str, replacement: object, message: str
) -> None:
    receipt = replay.build_control_receipt()
    receipt[field] = replacement
    with pytest.raises(verifier.ControlReceiptMismatch, match=message):
        verifier.verify_control_receipt(receipt, rerun=False)


def test_control_receipt_rejects_case_and_orbit_tamper() -> None:
    receipt = replay.build_control_receipt()
    tampered = copy.deepcopy(receipt)
    tampered["cases"][0]["engine_b_orbit_sha256"] = "0" * 64
    tampered["receipt_sha256"] = replay._sha256(
        {key: value for key, value in tampered.items() if key != "receipt_sha256"}
    )
    with pytest.raises(verifier.ControlReceiptMismatch, match="case digest"):
        verifier.verify_control_receipt(tampered, rerun=False)


def test_dpll_rejects_boolean_and_zero_assumptions() -> None:
    cnf = eb.build_factorization_cnf((0,), 1).cnf
    for assumption in (True, False, 0):
        with pytest.raises(ValueError, match="invalid literal"):
            eb.solve_cnf_dpll(cnf, (assumption,))
