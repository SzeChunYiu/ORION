from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from orion.discovery.jump_programme_closure import (
    JumpProgrammeTerminal,
    build_jump_programme_closure_report,
)
from orion.discovery.zero_error_jump_benchmark import (
    JumpArm,
    ZeroErrorJumpTerminal,
    build_zero_error_jump_benchmark_report,
)


ROOT = Path(__file__).resolve().parents[3]
RESEARCH = (
    ROOT
    / "research"
    / "extensions"
    / "orion-jump-recursive-atoms"
    / "zero_error_jump"
)
OWNERSHIP = RESEARCH / "JUMP_PROGRAMME_OWNERSHIP_V1.json"
PROGRAM_EXPECTED = RESEARCH / "JUMP_PROGRAMME_CLOSURE_EXPECTED_V1.json"
PROTOCOL = RESEARCH / "ZERO_ERROR_JUMP_PROTOCOL_V2.json"
JUMP_EXPECTED = RESEARCH / "ZERO_ERROR_JUMP_EXPECTED_V2.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _zero_error_report():
    return build_zero_error_jump_benchmark_report(
        protocol=_load(PROTOCOL),
        expected=_load(JUMP_EXPECTED),
    )


def _programme_report(
    *,
    ownership: dict[str, object] | None = None,
    expected: dict[str, object] | None = None,
):
    jump = _zero_error_report()
    parent = jump.primary.metric(JumpArm.VERIFIED_REGIME_REVISION_PARENT)
    orion = jump.primary.metric(JumpArm.ORION_JUMP)
    return build_jump_programme_closure_report(
        ownership=ownership or _load(OWNERSHIP),
        expected=expected or _load(PROGRAM_EXPECTED),
        local_zero_error_terminal=jump.terminal,
        local_zero_error_checks_passed=jump.all_checks_passed,
        strong_parent_matches_orion=(
            jump.verified_parent_equals_orion_decisions_primary
            and jump.verified_parent_equals_orion_decisions_replication
            and jump.verified_parent_equals_orion_metrics_primary
            and jump.verified_parent_equals_orion_metrics_replication
        ),
        orion_incremental_protected_gap=(
            orion.positive_jump_success - parent.positive_jump_success
        ),
    )


def test_jump_programme_scientific_packet_matches_registered_negative_terminal() -> None:
    expected = _load(PROGRAM_EXPECTED)
    assert expected["zero_error_benchmark_protocol"] == "ZeroErrorJumpProtocol.v2"

    report = _programme_report(expected=expected)
    assert report.deliverable_count == 11
    assert report.missing_deliverable_ids == ()
    assert report.paper_programme_owner_count == 10
    assert report.missing_paper_programme_ids == ()
    assert report.dependency_disposition_count == 14
    assert report.missing_child_dispositions == ()
    assert report.malformed_dependency_ids == ()
    assert report.generic_new_jump_atoms_claimed == 0
    assert report.composition_coordinate_count == 7
    assert (
        report.local_zero_error_terminal
        is ZeroErrorJumpTerminal.REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE
    )
    assert report.local_zero_error_checks_passed is True
    assert report.strong_parent_matches_orion is True
    assert report.orion_incremental_protected_gap == 0
    assert report.static_packet_certifies_merge_state is False
    assert report.scientific_packet_ready_for_external_integration is True
    assert (
        report.terminal
        is JumpProgrammeTerminal.REGIME_INVENTION_WITHOUT_INCREMENTAL_VALUE
    )
    assert report.grants_scientific_adoption is False
    assert report.grants_novelty_authority is False
    assert report.grants_issue_closure_authority is False
    assert report.certifies_dependency_ci_or_merge is False


def test_every_registered_500_deliverable_has_an_explicit_owner() -> None:
    ownership = _load(OWNERSHIP)
    deliverables = ownership["deliverables"]
    assert len(deliverables) == 11
    assert len({row["id"] for row in deliverables}) == 11
    assert all(row["owners"] for row in deliverables)
    assert all(row["status"] for row in deliverables)


def test_paper_programme_map_keeps_validation_transport_and_adoption_authority_external() -> None:
    ownership = _load(OWNERSHIP)
    by_id = {row["id"]: row for row in ownership["paper_programme_ownership"]}
    assert by_id["P3"]["jump_role"] == "CORRESPONDENCE_MAPPING_OBSTRUCTION"
    assert by_id["P7"]["jump_role"] == "SEMANTIC_TRANSPORT_PRESERVATION_REOPENING"
    assert "AUTHORITY" in by_id["P4"]["jump_role"]
    assert "AUTHORITY" in by_id["P8"]["jump_role"]
    assert "ADOPTION" in by_id["P5"]["jump_role"]
    assert by_id["HISTORICAL_ATLASES"]["update"] == "NEVER_PROTECTED_CONFIRMATORY_GOLD"


def test_programme_does_not_promote_any_generic_new_jump_atom() -> None:
    ownership = _load(OWNERSHIP)
    assert ownership["generic_new_jump_atoms_claimed"] == 0
    assert all(
        row["generic_new_jump_atom"] is False
        for row in ownership["composition_owners"]
    )


def test_missing_child_scientific_disposition_fails_closed() -> None:
    expected = _load(PROGRAM_EXPECTED)
    tampered = copy.deepcopy(expected)
    tampered["dependency_dispositions"] = [
        row for row in tampered["dependency_dispositions"] if row.get("issue") != 510
    ]
    report = _programme_report(expected=tampered)
    assert any(item.startswith("#510:") for item in report.missing_child_dispositions)
    assert report.scientific_packet_ready_for_external_integration is False
    assert report.terminal is JumpProgrammeTerminal.CANNOT_CHECK


def test_missing_deliverable_fails_closed() -> None:
    ownership = _load(OWNERSHIP)
    tampered = copy.deepcopy(ownership)
    tampered["deliverables"] = [
        row
        for row in tampered["deliverables"]
        if row["id"] != "EXECUTABLE_AXIOM_CORRESPONDENCE_OBJECT"
    ]
    report = _programme_report(ownership=tampered)
    assert report.missing_deliverable_ids == ("EXECUTABLE_AXIOM_CORRESPONDENCE_OBJECT",)
    assert report.terminal is JumpProgrammeTerminal.CANNOT_CHECK


def test_static_packet_cannot_self_attest_dependency_merge_state() -> None:
    expected = _load(PROGRAM_EXPECTED)
    tampered = copy.deepcopy(expected)
    tampered["integration_gate"]["static_packet_certifies_merge_state"] = True
    with pytest.raises(ValueError, match="merge state"):
        _programme_report(expected=tampered)


def test_generic_atom_self_promotion_is_rejected() -> None:
    ownership = _load(OWNERSHIP)
    tampered = copy.deepcopy(ownership)
    tampered["composition_owners"][0]["generic_new_jump_atom"] = True
    with pytest.raises(ValueError, match="generic Jump atom"):
        _programme_report(ownership=tampered)


def test_programme_terminal_depends_on_local_501_strong_parent_tie() -> None:
    ownership = _load(OWNERSHIP)
    expected = _load(PROGRAM_EXPECTED)
    report = build_jump_programme_closure_report(
        ownership=ownership,
        expected=expected,
        local_zero_error_terminal=ZeroErrorJumpTerminal.CANNOT_CHECK,
        local_zero_error_checks_passed=False,
        strong_parent_matches_orion=False,
        orion_incremental_protected_gap=1,
    )
    assert report.scientific_packet_ready_for_external_integration is False
    assert report.terminal is JumpProgrammeTerminal.CANNOT_CHECK
    assert report.grants_issue_closure_authority is False
