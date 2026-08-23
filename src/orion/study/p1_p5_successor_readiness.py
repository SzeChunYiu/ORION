"""Fail-closed readiness checks for the P1--P5 wide successors.

The checks in this module operate only on pre-outcome design artifacts.  A
``READY_FOR_EXTERNAL_BINDING`` report is not a scientific result and cannot be
used to promote a paper claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import sqrt
from pathlib import Path
from statistics import NormalDist
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class PowerAssessment:
    planned_independent_units: int
    minimum_independent_units: int
    projected_joint_power: float
    simultaneous_critical_value: float
    passes: bool


@dataclass(frozen=True)
class ProtocolAssessment:
    paper_id: str
    claim_id: str
    status: str
    blockers: tuple[str, ...]
    external_bindings_required: tuple[str, ...]
    power: PowerAssessment
    grants_scientific_authority: bool = False
    execution_authorized: bool = False
    execution_terminal: str = "CANNOT_CHECK_EXTERNAL_BINDINGS"

    def as_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "claim_id": self.claim_id,
            "status": self.status,
            "blockers": list(self.blockers),
            "external_bindings_required": list(self.external_bindings_required),
            "power": {
                "planned_independent_units": self.power.planned_independent_units,
                "minimum_independent_units": self.power.minimum_independent_units,
                "projected_joint_power": self.power.projected_joint_power,
                "simultaneous_critical_value": self.power.simultaneous_critical_value,
                "passes": self.power.passes,
            },
            "grants_scientific_authority": False,
            "execution_authorized": False,
            "execution_terminal": self.execution_terminal,
        }


def _joint_iut_power(
    *,
    n: int,
    true_delta: float,
    margin: float,
    discordance: float,
    comparator_count: int,
    alpha: float,
) -> tuple[float, float]:
    """Return joint power under the declared independent-contrast model.

    The calculation treats the independent source/task/project cluster as
    ``n``.  The paired difference is in ``{-1, 0, 1}``, so its variance is
    ``discordance - true_delta**2``.  The Sidak critical value is the exact
    max-T critical value under the prospectively declared independent-contrast
    planning model.  It is a planning model, not an analysis of protected
    outcomes or a universal worst-case correlation result.
    """

    if n <= 0 or comparator_count <= 0:
        raise ValueError("n and comparator_count must be positive")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between zero and one")
    if not 0.0 <= margin < true_delta <= 1.0:
        raise ValueError("planning requires 0 <= margin < true_delta <= 1")
    if not abs(true_delta) <= discordance <= 1.0:
        raise ValueError("discordance must be at least abs(true_delta) and at most one")

    normal = NormalDist()
    critical = normal.inv_cdf((1.0 - alpha) ** (1.0 / comparator_count))
    variance = discordance - true_delta**2
    standard_error = sqrt(variance / n)
    single_power = normal.cdf((true_delta - margin) / standard_error - critical)
    return single_power**comparator_count, critical


def assess_power(power: Mapping[str, Any], *, balanced_block_size: int) -> PowerAssessment:
    planned_n = int(power["planned_independent_units"])
    if "registered_simulated_minimum_independent_units" in power:
        minimum_n = int(power["registered_simulated_minimum_independent_units"])
        projected = float(power["registered_simulated_projected_joint_power"])
        critical = float(power["registered_simulated_critical_value"])
        return PowerAssessment(
            planned_independent_units=planned_n,
            minimum_independent_units=minimum_n,
            projected_joint_power=projected,
            simultaneous_critical_value=critical,
            passes=planned_n % balanced_block_size == 0 and planned_n >= minimum_n,
        )
    target = float(power["target_joint_power"])
    comparator_count = int(power["comparator_count"])
    params = {
        "true_delta": float(power["planning_delta"]),
        "margin": float(power["superiority_margin"]),
        "discordance": float(power["planning_discordance"]),
        "comparator_count": comparator_count,
        "alpha": float(power["familywise_alpha"]),
    }
    if balanced_block_size <= 0:
        raise ValueError("balanced block size must be positive")
    minimum_n = balanced_block_size
    while True:
        joint, critical = _joint_iut_power(n=minimum_n, **params)
        if joint >= target:
            break
        minimum_n += balanced_block_size
        if minimum_n > 100_000:
            raise ValueError("power target was not attainable within 100000 units")
    planned_power, planned_critical = _joint_iut_power(n=planned_n, **params)
    return PowerAssessment(
        planned_independent_units=planned_n,
        minimum_independent_units=minimum_n,
        projected_joint_power=planned_power,
        simultaneous_critical_value=planned_critical,
        passes=planned_n % balanced_block_size == 0 and planned_n >= minimum_n,
    )


def _content_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _check_local_bindings(
    root: Path, bindings: Sequence[Mapping[str, Any]], blockers: list[str]
) -> None:
    seen: set[str] = set()
    for binding in bindings:
        binding_id = str(binding.get("binding_id", ""))
        relative_path = str(binding.get("path", ""))
        digest = str(binding.get("sha256", ""))
        if not binding_id or binding_id in seen:
            blockers.append("local_binding_identity_missing_or_duplicate")
            continue
        seen.add(binding_id)
        path = root / relative_path
        if not path.is_file():
            blockers.append(f"local_binding_missing:{binding_id}")
        elif len(digest) != 64 or _content_sha256(path) != digest:
            blockers.append(f"local_binding_digest_mismatch:{binding_id}")


def _paper_specific_checks(protocol: Mapping[str, Any], blockers: list[str]) -> None:
    paper_id = protocol["paper_id"]
    design = protocol["design"]
    if paper_id == "P1":
        if int(design["stratum_count"]) != 32 or int(design["units_per_stratum"]) < 12:
            blockers.append("p1_r7a_not_wide_or_balanced")
        if int(protocol["power"]["comparator_count"]) != 9:
            blockers.append("p1_mandatory_comparator_family_incomplete")
    elif paper_id == "P2":
        if not design.get("matched_admissible_route_exposure"):
            blockers.append("p2_admissible_route_exposure_unmatched")
        if int(design.get("arena_count", 0)) < 2:
            blockers.append("p2_multi_arena_requirement_not_met")
        if not design.get("baseline_identity_reproduction_required"):
            blockers.append("p2_task_world_identity_not_required")
    elif paper_id == "P3":
        required = {"REFERENT", "CONSTRUCT", "MEASUREMENT", "TEMPORAL_CONTEXT"}
        if set(design.get("coordinates_with_required_nonzero_variation", ())) != required:
            blockers.append("p3_inert_coordinate_set_not_closed")
        if design.get("opportunity_rule") != "OBSERVATIONALLY_SEPARABLE_PROTECTED_DISTINCTION":
            blockers.append("p3_partial_identification_opportunity_rule_invalid")
    elif paper_id == "P4":
        if not design.get("paired_identifiable_control_required"):
            blockers.append("p4_naturalistic_pair_control_missing")
        if int(design.get("domain_count", 0)) < 4:
            blockers.append("p4_naturalistic_domain_width_insufficient")
    elif paper_id == "P5":
        required = {
            "EVIDENCE_REPAIR",
            "MEASUREMENT_REPAIR",
            "WITHIN_CLASS_MODEL_REPAIR",
            "MODEL_CLASS_EXPANSION",
            "REPRESENTATION_REGIME_REPAIR",
            "EXECUTION_REPAIR",
            "EVALUATOR_REPAIR",
            "UNRESOLVED",
        }
        if set(design.get("revision_classes", ())) != required:
            blockers.append("p5_revision_class_coverage_incomplete")
        if not design.get("same_visible_symptom_blocking_required"):
            blockers.append("p5_cause_confusable_blocking_missing")


def assess_protocol(protocol: Mapping[str, Any], *, root: Path) -> ProtocolAssessment:
    blockers: list[str] = []
    paper_id = str(protocol.get("paper_id", ""))
    claim_id = str(protocol.get("claim_id", ""))
    if paper_id not in {f"P{index}" for index in range(1, 6)}:
        blockers.append("paper_id_out_of_scope")
    if not claim_id:
        blockers.append("claim_id_missing")
    if protocol.get("outcomes_accessed") is not False:
        blockers.append("protected_outcomes_accessed_before_freeze")
    if protocol.get("grants_scientific_authority") is not False:
        blockers.append("preoutcome_protocol_claims_scientific_authority")
    if protocol.get("historical_results_immutable") is not True:
        blockers.append("historical_result_mutability_not_prohibited")
    if not protocol.get("successor_of"):
        blockers.append("successor_lineage_missing")

    design = protocol.get("design")
    if not isinstance(design, Mapping):
        raise ValueError("protocol design must be an object")
    independent_unit = str(design.get("independent_unit", ""))
    forbidden_units = {str(value) for value in design.get("not_independent_units", ())}
    if not independent_unit or independent_unit in forbidden_units:
        blockers.append("independent_unit_invalid")
    planned_n = int(design.get("planned_independent_units", 0))
    stratum_count = int(design.get("stratum_count", 0))
    units_per_stratum = int(design.get("units_per_stratum", 0))
    if planned_n != stratum_count * units_per_stratum:
        blockers.append("balanced_design_arithmetic_mismatch")

    power = assess_power(protocol["power"], balanced_block_size=stratum_count)
    if power.planned_independent_units != planned_n:
        blockers.append("power_and_design_sample_size_mismatch")
    if not power.passes:
        blockers.append("joint_power_or_balance_gate_not_met")

    bindings = protocol.get("local_bindings", ())
    if not isinstance(bindings, list) or not bindings:
        blockers.append("local_bindings_missing")
    else:
        _check_local_bindings(root, bindings, blockers)
    external = tuple(sorted({str(value) for value in protocol.get("external_bindings_required", ()) if value}))
    if not external:
        blockers.append("external_binding_boundary_missing")
    missing_external_terminal = str(protocol.get("missing_external_terminal", ""))
    if "CANNOT_CHECK" not in missing_external_terminal and "BLOCKED" not in missing_external_terminal:
        blockers.append("missing_external_terminal_not_fail_closed")

    _paper_specific_checks(protocol, blockers)
    blocker_tuple = tuple(sorted(set(blockers)))
    return ProtocolAssessment(
        paper_id=paper_id,
        claim_id=claim_id,
        status=(
            "READY_FOR_EXTERNAL_BINDING"
            if not blocker_tuple
            else "LOCAL_PREOUTCOME_CHECK_FAILED"
        ),
        blockers=blocker_tuple,
        external_bindings_required=external,
        power=power,
        execution_terminal=(
            "LOCAL_PREOUTCOME_CHECK_FAILED"
            if blocker_tuple
            else missing_external_terminal
        ),
    )


def load_and_assess(path: Path, *, root: Path) -> ProtocolAssessment:
    return assess_protocol(json.loads(path.read_text(encoding="utf-8")), root=root)


def validate_attainability_fixture(
    paper_id: str, fixture: Mapping[str, Any]
) -> tuple[str, ...]:
    """Validate synthetic, outcome-free fixtures that prove a gate can say yes and no."""

    errors: list[str] = []
    rows = fixture.get("rows")
    if not isinstance(rows, list) or not rows:
        return ("fixture_rows_missing",)
    clusters = [str(row.get("cluster_id", "")) for row in rows if isinstance(row, Mapping)]
    if len(clusters) != len(rows) or any(not value for value in clusters):
        errors.append("fixture_cluster_identity_missing")
    if len(set(clusters)) != len(clusters):
        errors.append("fixture_clusters_not_independent")
    if set(fixture.get("admissible_terminals", ())) != {"PASS", "FAIL"}:
        errors.append("fixture_gate_not_two_sided")

    if paper_id == "P3":
        required = {"REFERENT", "CONSTRUCT", "MEASUREMENT", "TEMPORAL_CONTEXT"}
        varied = {
            str(row.get("varied_coordinate", ""))
            for row in rows
            if isinstance(row, Mapping) and row.get("observationally_separable") is True
        }
        if varied != required:
            errors.append("p3_fixture_does_not_activate_all_four_coordinates")
        if not any(row.get("observationally_separable") is False for row in rows):
            errors.append("p3_fixture_lacks_identification_floor_control")
    elif paper_id == "P4":
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            if row.get("unidentifiable_expected") != "CANNOT_CHECK":
                errors.append("p4_fixture_unidentifiable_member_invalid")
            if row.get("identifiable_control_expected") != "RESOLVE":
                errors.append("p4_fixture_identifiable_control_invalid")
            if row.get("same_source_pair") is not True:
                errors.append("p4_fixture_pair_not_source_matched")
    elif paper_id == "P5":
        required = {
            "EVIDENCE_REPAIR",
            "MEASUREMENT_REPAIR",
            "WITHIN_CLASS_MODEL_REPAIR",
            "MODEL_CLASS_EXPANSION",
            "REPRESENTATION_REGIME_REPAIR",
            "EXECUTION_REPAIR",
            "EVALUATOR_REPAIR",
            "UNRESOLVED",
        }
        classes = {str(row.get("protected_revision_class", "")) for row in rows}
        if classes != required:
            errors.append("p5_fixture_revision_classes_incomplete")
        symptoms: dict[str, set[str]] = {}
        for row in rows:
            digest = str(row.get("candidate_visible_symptom_digest", ""))
            symptoms.setdefault(digest, set()).add(str(row.get("protected_revision_class", "")))
        if not symptoms or any(not digest or len(classes_) < 2 for digest, classes_ in symptoms.items()):
            errors.append("p5_fixture_not_cause_confusable_within_symptom_block")
    else:
        errors.append("fixture_paper_not_supported")
    return tuple(sorted(set(errors)))


__all__ = [
    "PowerAssessment",
    "ProtocolAssessment",
    "assess_power",
    "assess_protocol",
    "load_and_assess",
    "validate_attainability_fixture",
]
