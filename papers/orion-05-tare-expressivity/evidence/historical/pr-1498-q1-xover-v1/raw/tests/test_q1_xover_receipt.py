"""Tamper-evidence lock on the sole authoritative Q1-XOVER receipt.

`Q1_XOVER_RESULTS_V1.json` is the only receipt this study has: there is no
correction superseding it, so these tests are not a supersession guard. They pin
the receipt byte-exact, hold its recorded outcomes (including the negative) in
place, and assert that the two integrity chains embedded in the receipt — the
protocol hash and the runner hash — still match the committed files.

The recorded `P6_feasibility_rule = False` is preserved deliberately. Whether
its evaluator diverges from P6's registered statement is deferred to #1509
(defect-only frozen rerun, external authorization required) and #1508 (guard
asserting each prediction's evaluator matches its registered statement). Nothing
here re-evaluates P6.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIONQ = ROOT / "research/extensions/orion-q"
RECEIPT = ORIONQ / "Q1_XOVER_RESULTS_V1.json"
PROTOCOL = ORIONQ / "Q1_XOVER_PROTOCOL_V1.md"
RUNNER = ORIONQ / "q1_crossover_evaluation.py"

RECEIPT_SHA256 = "05eb59f6635ebccd8ebcebc79f3b9646aab6fce1d9852735c67d01f9cd3821f1"
DIRECT_DXX_MAX_N = 6


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _receipt() -> dict:
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_receipt_is_preserved_byte_exact() -> None:
    """The frozen receipt is never rewritten in place; corrections re-emit."""

    assert _sha256(RECEIPT) == RECEIPT_SHA256


def test_recorded_prediction_outcomes_are_held_in_place() -> None:
    """P1-P5 true, P6 false — preserved exactly as the runner emitted them."""

    outcomes = _receipt()["prediction_outcomes"]
    assert outcomes["P1_all_size_theorem"] is True
    assert outcomes["P2_sandwich"] is True
    assert outcomes["P3_family_size_identity"] is True
    assert outcomes["P4_witness_support"] is True
    assert outcomes["P5_r6q_identity_fresh_subject"] is True
    assert outcomes["P6_feasibility_rule"] is False


def test_recorded_verdict_is_held_in_place() -> None:
    """The verdict stands as emitted; see #1509 before changing this."""

    assert _receipt()["verdict"] == "RUN_INCOMPLETE"


def test_protocol_and_runner_hash_chains_still_match_committed_files() -> None:
    """Integrity gate 1: editing either file in place invalidates the receipt."""

    receipt = _receipt()
    assert receipt["protocol_sha256"] == _sha256(PROTOCOL)
    module_hashes = receipt["integrity"]["module_hashes"]
    assert module_hashes["q1_crossover_evaluation.py"] == _sha256(RUNNER)


def test_p6_false_is_reached_through_the_budget_clause_only() -> None:
    """Coverage accounting: the structural clause never fired in this panel.

    P6's evaluator is `timeouts == 0` AND a status check gated on
    `n > DIRECT_DXX_MAX_N`. No panel cell exceeds that bound, so the recorded
    `False` is attributable to the timeout clause alone. This documents the
    coverage limit; it does not assert what P6 would evaluate to if repaired.
    """

    panel = _receipt()["panel"]
    cells = [cell for cells in panel.values() for cell in cells]
    assert cells, "panel must not be empty"
    assert not [c for c in cells if c["n"] > DIRECT_DXX_MAX_N]
    assert sum(c["dxx_timeout_or_error"] for c in cells) == 12

    statuses = [row["dxx"]["status"] for c in cells for row in c["instances"]]
    assert statuses.count("TIMEOUT") == 12
    assert statuses.count("EXACT") == 372
