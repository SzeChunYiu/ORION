"""Execution adapter for P10 A0 protocol v1.1.

V1 froze the scientific families/arms before outcome access. Hostile review then
found that its declared same-surface/different-responsibility control was not
actually instantiated: surface ids and candidate presentation were keyed by the
family-specific world identity. This adapter preserves V1 as history while
executing the pre-outcome V1.1 amendment.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib

from . import a0_control as _base
from .a0_control import (
    A0Case,
    CandidateProposal,
    ControllerArm,
    EvaluationRecord,
    ProposalKind,
    Responsibility,
    derive_responsibility,
    evaluate_controller,
    predict,
)


_ORIGINAL_BUILD_CASE = _base.build_case
_ORIGINAL_CANDIDATE_PACKET = _base.candidate_packet


def _opaque(*parts: str, length: int = 16) -> str:
    raw = "|".join(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:length]


def build_case(
    responsibility: Responsibility,
    *,
    seed: str,
    surface_seed: str | None = None,
) -> A0Case:
    """Build a V1 case while allowing a responsibility-independent surface id."""

    case = _ORIGINAL_BUILD_CASE(responsibility, seed=seed)
    if surface_seed is None:
        return case
    return replace(case, surface_atom="s" + _opaque(surface_seed, "surface"))


def model_payload(case: A0Case) -> dict[str, object]:
    """Common typed controller payload; evaluator world identity is excluded."""

    payload = dict(_base.model_payload(case))
    payload.pop("world_id", None)
    return payload


def candidate_packet(
    case: A0Case,
    *,
    order_seed: str = "p10-a0-order-v1",
) -> tuple[CandidateProposal, ...]:
    """Keep per-world opaque candidate ids but equalize kind order by surface."""

    candidates = list(_ORIGINAL_CANDIDATE_PACKET(case, order_seed=order_seed))
    return tuple(
        sorted(
            candidates,
            key=lambda candidate: _opaque(
                order_seed,
                case.surface_atom,
                candidate.kind.value,
                "kind-order",
            ),
        )
    )


# Base predict/evaluate resolve candidate_packet through module globals at call
# time. Patching the execution adapter keeps frozen controller logic unchanged
# while enforcing the V1.1 presentation contract.
_base.candidate_packet = candidate_packet


def run_a0(
    *,
    seed: str = "p10-a0-responsibility-control-v1",
    cases_per_family: int = 128,
) -> dict[str, object]:
    if cases_per_family <= 0:
        raise ValueError("cases_per_family must be positive")

    cases: list[A0Case] = []
    family_counts: dict[str, int] = {}
    for index in range(cases_per_family):
        shared_surface_seed = _opaque(seed, str(index), "surface-group", length=32)
        for family_index, responsibility in enumerate(Responsibility):
            family_counts[responsibility.value] = cases_per_family
            case_seed = _opaque(seed, str(family_index), str(index), "case", length=32)
            cases.append(
                build_case(
                    responsibility,
                    seed=case_seed,
                    surface_seed=shared_surface_seed,
                )
            )

    unresolved_total = sum(
        int(derive_responsibility(case) is Responsibility.UNRESOLVED) for case in cases
    )
    arms: dict[str, dict[str, object]] = {}
    for arm in ControllerArm:
        records = [evaluate_controller(case, predict(arm, case)) for case in cases]
        rows = tuple(records)
        n = len(rows)
        unresolved_correct = sum(int(row.unresolved_correct) for row in rows)
        arms[arm.value] = {
            "sample_count": n,
            "accuracy": sum(int(row.correct) for row in rows) / n if n else None,
            "unnecessary_reframe_rate": sum(int(row.unnecessary_reframe) for row in rows) / n if n else None,
            "false_closure_rate": sum(int(row.false_closure) for row in rows) / n if n else None,
            "invalid_action_rate": sum(int(row.invalid_action) for row in rows) / n if n else None,
            "unresolved_accuracy": unresolved_correct / unresolved_total if unresolved_total else None,
            "mean_decision_cost_units": sum(row.cost_units for row in rows) / n if n else None,
        }

    orion = arms[ControllerArm.ORION_RESPONSIBILITY_CONTROL.value]
    donor = arms[ControllerArm.DONOR_COMPOSED_CONTROL.value]
    symbolic = arms[ControllerArm.SYMBOLIC_FEASIBILITY_CONTROL.value]
    dependency = arms[ControllerArm.DEPENDENCY_SUPPORT_CONTROL.value]
    serialized = arms[ControllerArm.SERIALIZED_STATE_RULE.value]

    if serialized["accuracy"] == 1.0:
        terminal = "P10_NO_CONTROL_RESIDUAL"
    elif (
        symbolic["accuracy"] is not None
        and dependency["accuracy"] is not None
        and max(float(symbolic["accuracy"]), float(dependency["accuracy"]))
        >= float(orion["accuracy"]) - 0.02
        and max(
            float(symbolic["false_closure_rate"]),
            float(dependency["false_closure_rate"]),
        )
        <= float(orion["false_closure_rate"])
    ):
        terminal = "P10_GRAPH_OR_SYMBOLIC_CONTROL_SUFFICIENT"
    elif (
        abs(float(donor["accuracy"]) - float(orion["accuracy"])) <= 0.02
        and float(donor["false_closure_rate"]) <= float(orion["false_closure_rate"])
        and float(donor["unnecessary_reframe_rate"])
        <= float(orion["unnecessary_reframe_rate"])
    ):
        terminal = "P10_EXISTING_STRUCTURED_CONTROL_SUFFICIENT"
    elif (
        float(orion["accuracy"]) == 1.0
        and float(orion["accuracy"]) - float(donor["accuracy"]) >= 0.10
    ):
        terminal = "P10_RESPONSIBILITY_CONTROL_INCREMENTAL_VALUE"
    else:
        terminal = "CANNOT_CHECK"

    # Verify the registered V1.1 surface hostility mechanically on the execution
    # corpus. Each index contributes one case per responsibility with one shared
    # surface token and identical candidate-kind presentation.
    surface_groups: dict[str, list[A0Case]] = {}
    for case in cases:
        surface_groups.setdefault(case.surface_atom, []).append(case)
    surface_contract_green = all(
        len(group) == len(Responsibility)
        and len({derive_responsibility(case) for case in group}) == len(Responsibility)
        and len(
            {
                tuple(candidate.kind for candidate in candidate_packet(case))
                for case in group
            }
        )
        == 1
        for group in surface_groups.values()
    )
    if not surface_contract_green:
        terminal = "CANNOT_CHECK"

    return {
        "schema": "P10.A0ResponsibilityControlResult.v1.1",
        "protocol": "P10.A0ResponsibilityControlProtocol.v1.1",
        "seed_digest": "sha256:" + hashlib.sha256(seed.encode("utf-8")).hexdigest(),
        "cases_per_family": cases_per_family,
        "family_counts": family_counts,
        "surface_group_count": len(surface_groups),
        "same_surface_hostile_contract_green": surface_contract_green,
        "arms": arms,
        "terminal": terminal,
        "claim_ceiling": "finite exact fixed-proposal responsibility-routing worlds only",
        "scientific_authority": "NONE_BOUNDED_DIAGNOSTIC",
        "grants_live_llm_escalation": terminal
        == "P10_RESPONSIBILITY_CONTROL_INCREMENTAL_VALUE",
    }


__all__ = [
    "A0Case",
    "CandidateProposal",
    "ControllerArm",
    "EvaluationRecord",
    "ProposalKind",
    "Responsibility",
    "build_case",
    "candidate_packet",
    "derive_responsibility",
    "evaluate_controller",
    "model_payload",
    "predict",
    "run_a0",
]
