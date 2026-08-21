#!/usr/bin/env python3
"""Fail-closed verifier for the frozen MAX-R6 exact TARE-3 development lane.

This verifier is deliberately separate from the scientific solver. It binds the
post-freeze gate-enforcement errata and rejects any positive development receipt
whose open-subject panel is incomplete. It never reads the protected stretched
N2 subject.
"""
from __future__ import annotations

import json
from typing import Any

REQUIRED_SUBJECTS = ("H4", "N2")
TOP_K = 4
BOUND_ERRATA = (
    "MAX_R6_EXACT_TARE3_DP_ERRATUM_1",
    "MAX_R6_EXACT_TARE3_DP_ERRATUM_2",
    "MAX_R6_EXACT_TARE3_DP_ERRATUM_3",
)


def _truth_conjunction(mapping: dict[str, Any]) -> bool:
    return bool(mapping) and all(value is True for value in mapping.values())


def verify_result(result: dict[str, Any]) -> dict[str, Any]:
    """Return a fail-closed verification receipt for one solver result."""

    errors: list[str] = []
    gates = result.get("gates")
    if not isinstance(gates, dict):
        gates = {}
        errors.append("missing_or_invalid_gates")

    if result.get("reserved_stretched_n2_accessed") is not False:
        errors.append("protected_stretched_n2_access_not_false")

    p10_replay = result.get("p10_replay")
    if not isinstance(p10_replay, dict):
        p10_replay = {}
        errors.append("missing_or_invalid_p10_replay")
    elif p10_replay.get("reserved_stretched_n2_accessed") is not False:
        errors.append("p10_protected_stretched_n2_access_not_false")

    protocol_errata_raw = result.get("protocol_errata")
    if not isinstance(protocol_errata_raw, (list, tuple)) or any(
        not isinstance(item, str) for item in protocol_errata_raw
    ):
        protocol_errata: list[str] = []
        errors.append("missing_or_invalid_protocol_errata")
    else:
        protocol_errata = list(protocol_errata_raw)
    missing_errata = [item for item in BOUND_ERRATA if item not in protocol_errata]
    if missing_errata:
        errors.append("underlying_receipt_missing_bound_errata:" + ",".join(missing_errata))

    underlying_supported = result.get("development_supported") is True
    underlying_conjunction = _truth_conjunction(gates)
    if underlying_supported != underlying_conjunction:
        errors.append("development_supported_not_equal_to_declared_gate_conjunction")

    expected_authority = (
        "MAX_R6_EXACT_TARE3_JOINT_DP_SUPPORTED"
        if underlying_supported
        else "MAX_R6_EXACT_TARE3_JOINT_DP_NEGATIVE"
    )
    if result.get("authority") != expected_authority:
        errors.append("authority_not_equal_to_declared_support_state")

    subjects = result.get("subjects")
    if not isinstance(subjects, dict):
        subjects = {}
        errors.append("missing_or_invalid_subjects")

    p10_generated = p10_replay.get("candidate_generated") is True
    if p10_generated and set(subjects) != set(REQUIRED_SUBJECTS):
        errors.append("p10_positive_without_exact_required_open_subject_set")

    panel_details: dict[str, Any] = {}
    panel_complete = True
    for name in REQUIRED_SUBJECTS:
        subject = subjects.get(name)
        if not isinstance(subject, dict):
            panel_details[name] = {
                "present": False,
                "selected_top_k": None,
                "selected_count": None,
                "triple_count": None,
                "complete": False,
            }
            panel_complete = False
            continue

        triples = subject.get("triples")
        triple_count = len(triples) if isinstance(triples, list) else None
        complete = (
            subject.get("selected_top_k") == TOP_K
            and subject.get("selected_count") == TOP_K
            and triple_count == TOP_K
        )
        panel_details[name] = {
            "present": True,
            "selected_top_k": subject.get("selected_top_k"),
            "selected_count": subject.get("selected_count"),
            "triple_count": triple_count,
            "complete": complete,
            "all_witnesses_valid": subject.get("all_witnesses_valid"),
        }
        panel_complete = panel_complete and complete

        if complete and subject.get("all_witnesses_valid") is not True:
            errors.append(f"{name}_complete_panel_without_valid_witnesses")

    declared_panel_gate = gates.get("top_four_panel_complete")
    if not isinstance(declared_panel_gate, bool):
        errors.append("missing_or_invalid_declared_top_four_panel_gate")
    elif declared_panel_gate is not panel_complete:
        errors.append("declared_top_four_panel_gate_disagrees_with_recomputed_panel")

    # Erratum 3 is a controlling frozen gate. A positive underlying receipt with
    # a short panel is therefore a fail-open scientific-integrity error, not a
    # legitimate negative experimental outcome.
    if underlying_supported and not panel_complete:
        errors.append("positive_underlying_receipt_with_incomplete_top_four_panel")

    strict_gates = dict(gates)
    strict_gates["top_four_panel_complete"] = panel_complete
    strict_supported = _truth_conjunction(strict_gates)

    # If P10 did not generate a candidate, absence of panels is a legitimate
    # negative path. It is not a software-integrity error, but it cannot be
    # pre-prospective-ready.
    if not p10_generated:
        strict_supported = False

    software_integrity_pass = not errors
    pre_prospective_ready = software_integrity_pass and strict_supported

    return {
        "schema": "ORIONQ.MAXR6.ExactTARE3EndToEndVerification.v1",
        "authority": (
            "EXACT_TARE3_PRE_PROSPECTIVE_READY__PROTECTED_N2_STILL_CLOSED"
            if pre_prospective_ready
            else "EXACT_TARE3_NOT_PRE_PROSPECTIVE_READY__PROTECTED_N2_STILL_CLOSED"
        ),
        "scope": "OPEN_H4_EQ_N2_VERIFICATION_ONLY__NOT_R6",
        "bound_errata": list(BOUND_ERRATA),
        "underlying_protocol_errata": protocol_errata,
        "underlying_erratum3_listed": (
            "MAX_R6_EXACT_TARE3_DP_ERRATUM_3" in protocol_errata
        ),
        "required_subjects": list(REQUIRED_SUBJECTS),
        "required_top_k": TOP_K,
        "panel_details": panel_details,
        "top_four_panel_complete": panel_complete,
        "declared_gates": gates,
        "strict_gates": strict_gates,
        "underlying_supported": underlying_supported,
        "strict_supported": strict_supported,
        "software_integrity_pass": software_integrity_pass,
        "pre_prospective_ready": pre_prospective_ready,
        "reserved_stretched_n2_accessed": False,
        "errors": errors,
    }


def main() -> dict[str, Any]:
    # Local import keeps verify_result cheap and independently unit-testable.
    import max_r6_exact_tare3_joint_frame_dp as solver

    result = solver.main()
    verified = verify_result(result)
    print(
        "ORIONQ_MAX_R6_EXACT_TARE3_E2E_VERIFY="
        + json.dumps(verified, sort_keys=True)
    )
    if not verified["software_integrity_pass"]:
        raise SystemExit(2)
    return verified


if __name__ == "__main__":
    main()
