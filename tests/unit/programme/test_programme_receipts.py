"""Epoch manifests, longitudinal claims, and programme receipts stay empty."""

from __future__ import annotations

from dataclasses import replace

from orion.programme.activation import UNBOUND_DIGEST
from orion.programme.epoch_manifest import (
    epoch_manifest_payload,
    unexecuted_epoch_manifest,
    validate_epoch_manifest,
)
from orion.programme.identity import verify_seal
from orion.programme.longitudinal import (
    LONGITUDINAL_CLAIMS,
    assess_longitudinal,
    longitudinal_payload,
    unexecuted_longitudinal_evidence,
    validate_longitudinal_evidence,
)
from orion.programme.receipts import (
    archival_strategy_payload,
    programme_receipt_payload,
    regenerate_programme_trajectory,
    unexecuted_programme_receipt,
    validate_archival_strategy,
    validate_programme_receipt,
)
from orion.programme.records import Outcome


def test_unexecuted_epoch_is_valid_and_sealed() -> None:
    manifest = unexecuted_epoch_manifest()
    assert validate_epoch_manifest(manifest) == ()
    payload = epoch_manifest_payload(manifest)
    assert verify_seal(payload) == ()
    assert payload["live_epoch"] is False
    assert payload["frozen"] is False


def test_frozen_or_populated_epoch_is_refused() -> None:
    frozen = replace(unexecuted_epoch_manifest(), frozen=True)
    assert "an epoch cannot be frozen while programme activation is withheld" in validate_epoch_manifest(frozen)
    populated = replace(unexecuted_epoch_manifest(), cycle_receipt_ids=("cycle-1",))
    assert any("cycle receipts" in item for item in validate_epoch_manifest(populated))
    bound = replace(unexecuted_epoch_manifest(), evaluator_artifact_hash="a" * 64)
    assert any("unbound" in item for item in validate_epoch_manifest(bound))


def test_longitudinal_evidence_is_cannot_check_on_zero_epochs() -> None:
    evidence = unexecuted_longitudinal_evidence()
    assert len(LONGITUDINAL_CLAIMS) == 8
    assert validate_longitudinal_evidence(evidence) == ()
    assert assess_longitudinal(evidence) is Outcome.CANNOT_CHECK
    assert assess_longitudinal() is Outcome.CANNOT_CHECK
    assert evidence.grants_phase4_closure is False
    payload = longitudinal_payload(evidence)
    assert verify_seal(payload) == ()
    assert payload["evidence_status"] == "NO_PROTECTED_EVIDENCE"
    assert all(value == "CANNOT_CHECK" for value in payload["claims"].values())


def test_longitudinal_pass_without_epochs_is_refused() -> None:
    evidence = replace(
        unexecuted_longitudinal_evidence(),
        claims=tuple((name, Outcome.PASS) for name in LONGITUDINAL_CLAIMS),
    )
    errors = validate_longitudinal_evidence(evidence)
    assert any("cannot PASS with zero evaluation epochs" in item for item in errors)
    assert assess_longitudinal(evidence) is Outcome.CANNOT_CHECK


def test_longitudinal_never_returns_pass() -> None:
    fabricated = replace(
        unexecuted_longitudinal_evidence(),
        epoch_count=2,
        claims=tuple((name, Outcome.PASS) for name in LONGITUDINAL_CLAIMS),
    )
    assert assess_longitudinal(fabricated) is not Outcome.PASS
    assert fabricated.grants_phase4_closure is False


def test_programme_receipt_and_archive_are_inert() -> None:
    receipt = unexecuted_programme_receipt()
    assert validate_programme_receipt(receipt) == ()
    assert receipt.grants_phase4_closure is False
    payload = programme_receipt_payload(receipt)
    assert verify_seal(payload) == ()
    assert payload["cycles_executed"] == 0
    archive = archival_strategy_payload()
    assert verify_seal(archive) == ()
    assert validate_archival_strategy(archive) == ()
    assert archive["live_archive_populated"] is False


def test_programme_receipt_rejects_fabricated_ci_green() -> None:
    receipt = replace(unexecuted_programme_receipt(), ci_green=True, exact_final_head="abc")
    errors = validate_programme_receipt(receipt)
    assert "exact-final-head CI cannot be declared green from preparatory scaffolding" in errors
    assert "exact_final_head must remain empty until a terminal promotion attempt" in errors


def test_regenerator_refuses_to_invent_a_trajectory() -> None:
    assert regenerate_programme_trajectory() is Outcome.CANNOT_CHECK
    assert regenerate_programme_trajectory(("cycle-1",)) is Outcome.FAIL
    assert UNBOUND_DIGEST == "0" * 64
