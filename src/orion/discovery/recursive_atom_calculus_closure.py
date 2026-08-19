"""Finite, non-authorizing closure checks for recursive atom-study issue #507.

The module closes only the *study calculus*: ownership coverage, a common result
vocabulary, recursion stop reasons, negative-history export categories, stable
post-map saturation declarations, and a small interaction protocol that calls
the actual #513 set-level interaction bookkeeping.

It does not decide scientific atoms from raw science, execute Jump candidates,
or grant novelty/adoption/issue-closure authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from orion.transfer.v2.bounded_epistemic_study import analyze_contract_interaction
from orion.transfer.v2.canonical import content_digest


class RecursiveAtomCalculusTerminal(str, Enum):
    RECURSIVE_ATOM_STUDY_CALCULUS_FROZEN = "RECURSIVE_ATOM_STUDY_CALCULUS_FROZEN"
    CANNOT_CHECK = "CANNOT_CHECK"


class AtomStudyDisposition(str, Enum):
    SUBSUMED = "SUBSUMED"
    ATOM_INCREMENTAL_VALUE = "ATOM_INCREMENTAL_VALUE"
    INTERACTION_ONLY = "INTERACTION_ONLY"
    REDUNDANT_EQUIVALENT = "REDUNDANT_EQUIVALENT"
    DOMAIN_SPECIFIC = "DOMAIN_SPECIFIC"
    OVERREACH_HARMFUL = "OVERREACH_HARMFUL"
    NON_IDENTIFIABLE = "NON_IDENTIFIABLE"
    NO_INCREMENTAL_VALUE = "NO_INCREMENTAL_VALUE"
    CANNOT_CHECK = "CANNOT_CHECK"
    IRREDUCIBLE_AT_CURRENT_RESOLUTION = "IRREDUCIBLE_AT_CURRENT_RESOLUTION"


class RecursionStopReason(str, Enum):
    DONOR_OR_EXISTING_FORMALISM_SUBSUMES = "DONOR_OR_EXISTING_FORMALISM_SUBSUMES"
    NO_PROTECTED_DISCRIMINATOR = "NO_PROTECTED_DISCRIMINATOR"
    IMPLEMENTATION_DETAIL_NO_BOUNDED_EFFECT = "IMPLEMENTATION_DETAIL_NO_BOUNDED_EFFECT"
    NONUNIQUE_OBSERVATIONALLY_EQUIVALENT_DECOMPOSITION = (
        "NONUNIQUE_OBSERVATIONALLY_EQUIVALENT_DECOMPOSITION"
    )
    INTERACTION_TERM_ONLY = "INTERACTION_TERM_ONLY"
    INACCESSIBLE_PRIVATE_COGNITIVE_VARIABLE = "INACCESSIBLE_PRIVATE_COGNITIVE_VARIABLE"
    ANECDOTE_SPECIFIC_OVERDECOMPOSITION = "ANECDOTE_SPECIFIC_OVERDECOMPOSITION"


class NegativeHistoryCategory(str, Enum):
    FAILED_DEFINITION = "FAILED_DEFINITION"
    FAILED_DECOMPOSITION = "FAILED_DECOMPOSITION"
    NULL_ABLATION = "NULL_ABLATION"
    HARMFUL_OVERUSE = "HARMFUL_OVERUSE"
    DONOR_SUBSUMPTION = "DONOR_SUBSUMPTION"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    INACTIVE_NO_ATOM_CONDITION = "INACTIVE_NO_ATOM_CONDITION"
    UNRESOLVED_OR_NON_IDENTIFIABLE = "UNRESOLVED_OR_NON_IDENTIFIABLE"


@dataclass(frozen=True)
class PostMapSaturationRound:
    round_id: str
    primary_source_ids: tuple[str, ...]
    material_change: bool
    mapped_family_ids: tuple[str, ...]

    def verify(self) -> None:
        if not self.round_id or not self.primary_source_ids or not self.mapped_family_ids:
            raise ValueError("saturation round requires identity, sources, and mapped families")
        if any(not item for item in self.primary_source_ids + self.mapped_family_ids):
            raise ValueError("saturation round identities must be non-empty")


_POST_MAP_ROUNDS: tuple[PostMapSaturationRound, ...] = (
    PostMapSaturationRound(
        round_id="POST_MAP_ROUND_1",
        primary_source_ids=(
            "arxiv:2311.03893",
            "arxiv:2603.19782",
            "arxiv:2506.21329",
        ),
        material_change=False,
        mapped_family_ids=(
            "AFFORDANCE_FUNCTION_STATE",
            "CHANGE_OBSERVATION_INTERVENTION_INTERFACE",
            "IMAGINATION_COUNTERFACTUAL_EXPERIENCE",
        ),
    ),
    PostMapSaturationRound(
        round_id="POST_MAP_ROUND_2",
        primary_source_ids=(
            "arxiv:2607.05682",
            "arxiv:2211.16605",
            "arxiv:2310.19791",
            "arxiv:2608.02505",
        ),
        material_change=False,
        mapped_family_ids=(
            "QUESTION_CONJECTURE_PROBLEM_TASTE",
            "MUTABLE_OPERATOR_LANGUAGE",
            "ANALOGY_CORRESPONDENCE_WORKSPACE",
        ),
    ),
)


@dataclass(frozen=True)
class InteractionWitnessCase:
    case_id: str
    left_atom_id: str
    right_atom_id: str
    left_delta_contract_ids: tuple[str, ...]
    right_delta_contract_ids: tuple[str, ...]
    combined_delta_contract_ids: tuple[str, ...]
    observationally_separable: bool
    donor_subsumes: bool
    expected_disposition: AtomStudyDisposition

    def verify(self) -> None:
        if not self.case_id or not self.left_atom_id or not self.right_atom_id:
            raise ValueError("interaction witness requires case and atom identities")
        if self.left_atom_id == self.right_atom_id:
            raise ValueError("interaction witness requires distinct proposed atoms")


_INTERACTION_WITNESSES: tuple[InteractionWitnessCase, ...] = (
    InteractionWitnessCase(
        case_id="independent-left-effect",
        left_atom_id="a",
        right_atom_id="b",
        left_delta_contract_ids=("left-only-contract",),
        right_delta_contract_ids=(),
        combined_delta_contract_ids=("left-only-contract",),
        observationally_separable=True,
        donor_subsumes=False,
        expected_disposition=AtomStudyDisposition.ATOM_INCREMENTAL_VALUE,
    ),
    InteractionWitnessCase(
        case_id="interaction-only-synergy",
        left_atom_id="a",
        right_atom_id="b",
        left_delta_contract_ids=(),
        right_delta_contract_ids=(),
        combined_delta_contract_ids=("synergy-contract",),
        observationally_separable=True,
        donor_subsumes=False,
        expected_disposition=AtomStudyDisposition.INTERACTION_ONLY,
    ),
    InteractionWitnessCase(
        case_id="redundant-equivalent-children",
        left_atom_id="a",
        right_atom_id="b",
        left_delta_contract_ids=("shared-contract",),
        right_delta_contract_ids=("shared-contract",),
        combined_delta_contract_ids=("shared-contract",),
        observationally_separable=True,
        donor_subsumes=False,
        expected_disposition=AtomStudyDisposition.REDUNDANT_EQUIVALENT,
    ),
    InteractionWitnessCase(
        case_id="shared-standalone-value-lossy-combination",
        left_atom_id="a",
        right_atom_id="b",
        left_delta_contract_ids=("shared-a", "shared-b"),
        right_delta_contract_ids=("shared-a", "shared-b"),
        combined_delta_contract_ids=("shared-a",),
        observationally_separable=True,
        donor_subsumes=False,
        expected_disposition=AtomStudyDisposition.OVERREACH_HARMFUL,
    ),
    InteractionWitnessCase(
        case_id="observationally-non-identifiable-children",
        left_atom_id="a",
        right_atom_id="b",
        left_delta_contract_ids=("left-surface",),
        right_delta_contract_ids=("right-surface",),
        combined_delta_contract_ids=("left-surface", "right-surface"),
        observationally_separable=False,
        donor_subsumes=False,
        expected_disposition=AtomStudyDisposition.NON_IDENTIFIABLE,
    ),
)


def common_result_dispositions() -> tuple[AtomStudyDisposition, ...]:
    return tuple(AtomStudyDisposition)


def recursion_stop_reasons() -> tuple[RecursionStopReason, ...]:
    return tuple(RecursionStopReason)


def negative_history_categories() -> tuple[NegativeHistoryCategory, ...]:
    return tuple(NegativeHistoryCategory)


def post_map_saturation_rounds() -> tuple[PostMapSaturationRound, ...]:
    return _POST_MAP_ROUNDS


def interaction_witness_cases() -> tuple[InteractionWitnessCase, ...]:
    return _INTERACTION_WITNESSES


def classify_interaction_witness(case: InteractionWitnessCase) -> AtomStudyDisposition:
    """Classify one bounded two-child interaction witness.

    Inputs are already deltas against the frozen no-child regime. The function
    uses #513's actual set-level interaction bookkeeping and then applies #507's
    fail-closed scientific vocabulary. Standalone reach is measured against the
    no-child baseline; left-vs-right set difference is not a substitute for that
    baseline comparison. A combination that destroys a contract reachable by
    either child is explicitly harmful overreach.
    """

    case.verify()
    if not case.observationally_separable:
        return AtomStudyDisposition.NON_IDENTIFIABLE
    if case.donor_subsumes:
        return AtomStudyDisposition.SUBSUMED

    report = analyze_contract_interaction(
        left_atom_id=case.left_atom_id,
        right_atom_id=case.right_atom_id,
        left_reachable_contract_ids=case.left_delta_contract_ids,
        right_reachable_contract_ids=case.right_delta_contract_ids,
        combined_reachable_contract_ids=case.combined_delta_contract_ids,
    )
    report.verify()
    if report.grants_atom_independence_claim:
        raise AssertionError("#513 interaction bookkeeping must remain non-authorizing")

    if report.synergy_contract_ids and not (
        case.left_delta_contract_ids or case.right_delta_contract_ids
    ):
        return AtomStudyDisposition.INTERACTION_ONLY
    if (
        set(case.left_delta_contract_ids) == set(case.right_delta_contract_ids)
        and set(case.combined_delta_contract_ids) == set(case.left_delta_contract_ids)
        and bool(case.left_delta_contract_ids)
    ):
        return AtomStudyDisposition.REDUNDANT_EQUIVALENT
    if report.lost_in_combination_contract_ids and (
        case.left_delta_contract_ids or case.right_delta_contract_ids
    ):
        return AtomStudyDisposition.OVERREACH_HARMFUL
    if report.left_only_contract_ids or report.right_only_contract_ids:
        return AtomStudyDisposition.ATOM_INCREMENTAL_VALUE
    if report.shared_individual_contract_ids and (
        case.left_delta_contract_ids or case.right_delta_contract_ids
    ):
        return AtomStudyDisposition.ATOM_INCREMENTAL_VALUE
    if report.synergy_contract_ids:
        return AtomStudyDisposition.ATOM_INCREMENTAL_VALUE
    return AtomStudyDisposition.NO_INCREMENTAL_VALUE


def _validate_ownership_map(
    ownership_map: Mapping[str, object],
) -> tuple[int, int, int, int, tuple[str, ...]]:
    coordinate_rows = tuple(ownership_map.get("candidate_coordinates", ()))
    transform_rows = tuple(ownership_map.get("candidate_transformations", ()))
    existing_rows = tuple(ownership_map.get("existing_orion_owners", ()))
    generic_claimed = int(ownership_map.get("generic_new_atoms_claimed", -1))

    if not coordinate_rows or not transform_rows or not existing_rows:
        raise ValueError("ownership map must cover coordinates, transformations, and owners")

    missing: list[str] = []
    coordinate_ids: list[str] = []
    for raw in coordinate_rows:
        if not isinstance(raw, Mapping):
            raise ValueError("candidate coordinate rows must be objects")
        row_id = str(raw.get("id", ""))
        coordinate_ids.append(row_id)
        if not row_id or not raw.get("disposition") or not raw.get("owner"):
            missing.append(row_id or "<coordinate-without-id>")
        if raw.get("generic_orion_atom_claim") is not False:
            raise ValueError("candidate coordinate cannot self-declare a generic ORION atom")

    transform_ids: list[str] = []
    for raw in transform_rows:
        if not isinstance(raw, Mapping):
            raise ValueError("candidate transformation rows must be objects")
        row_id = str(raw.get("id", ""))
        transform_ids.append(row_id)
        if not row_id or not raw.get("disposition") or not raw.get("owner"):
            missing.append(row_id or "<transformation-without-id>")

    owner_ids: list[str] = []
    for raw in existing_rows:
        if not isinstance(raw, Mapping):
            raise ValueError("existing owner rows must be objects")
        row_id = str(raw.get("atom", ""))
        owner_ids.append(row_id)
        if not row_id or not raw.get("owner"):
            missing.append(row_id or "<owner-without-id>")

    for label, ids in (
        ("coordinate", coordinate_ids),
        ("transformation", transform_ids),
        ("existing-owner", owner_ids),
    ):
        if len(ids) != len(set(ids)):
            raise ValueError(f"duplicate {label} identity in ownership map")

    if generic_claimed != 0:
        raise ValueError("ownership map must not manufacture generic new atoms")

    return (
        len(coordinate_rows),
        len(transform_rows),
        len(existing_rows),
        generic_claimed,
        tuple(sorted(set(missing))),
    )


@dataclass(frozen=True)
class RecursiveAtomCalculusClosureReport:
    candidate_coordinate_count: int
    candidate_transformation_count: int
    existing_owner_count: int
    generic_new_atoms_claimed: int
    ownership_missing_rows: tuple[str, ...]
    post_map_round_count: int
    post_map_material_change_round_ids: tuple[str, ...]
    common_result_disposition_count: int
    recursion_stop_reason_count: int
    negative_history_category_count: int
    interaction_witness_count: int
    interaction_mismatched_case_ids: tuple[str, ...]
    terminal: RecursiveAtomCalculusTerminal
    all_checks_passed: bool
    digest: str

    @property
    def grants_scientific_atom_authority(self) -> bool:
        return False

    @property
    def grants_jump_authority(self) -> bool:
        return False

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    @property
    def grants_issue_closure_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "RecursiveAtomCalculusClosureReport.v1",
            "candidate_coordinate_count": self.candidate_coordinate_count,
            "candidate_transformation_count": self.candidate_transformation_count,
            "existing_owner_count": self.existing_owner_count,
            "generic_new_atoms_claimed": self.generic_new_atoms_claimed,
            "ownership_missing_rows": list(self.ownership_missing_rows),
            "post_map_round_count": self.post_map_round_count,
            "post_map_material_change_round_ids": list(
                self.post_map_material_change_round_ids
            ),
            "common_result_disposition_count": self.common_result_disposition_count,
            "recursion_stop_reason_count": self.recursion_stop_reason_count,
            "negative_history_category_count": self.negative_history_category_count,
            "interaction_witness_count": self.interaction_witness_count,
            "interaction_mismatched_case_ids": list(self.interaction_mismatched_case_ids),
            "terminal": self.terminal.value,
            "all_checks_passed": self.all_checks_passed,
            "grants_scientific_atom_authority": False,
            "grants_jump_authority": False,
            "grants_novelty_authority": False,
            "grants_issue_closure_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("recursive atom calculus closure digest mismatch")


def build_recursive_atom_calculus_closure_report(
    ownership_map: Mapping[str, object],
) -> RecursiveAtomCalculusClosureReport:
    (
        coordinate_count,
        transform_count,
        existing_count,
        generic_claimed,
        missing_rows,
    ) = _validate_ownership_map(ownership_map)

    material_change_round_ids: list[str] = []
    for round_record in _POST_MAP_ROUNDS:
        round_record.verify()
        if round_record.material_change:
            material_change_round_ids.append(round_record.round_id)

    mismatched: list[str] = []
    for case in _INTERACTION_WITNESSES:
        actual = classify_interaction_witness(case)
        if actual is not case.expected_disposition:
            mismatched.append(case.case_id)

    all_checks_passed = (
        coordinate_count == 12
        and transform_count == 18
        and existing_count == 11
        and generic_claimed == 0
        and not missing_rows
        and len(_POST_MAP_ROUNDS) == 2
        and not material_change_round_ids
        and len(tuple(AtomStudyDisposition)) == 10
        and len(tuple(RecursionStopReason)) == 7
        and len(tuple(NegativeHistoryCategory)) == 8
        and len(_INTERACTION_WITNESSES) == 5
        and not mismatched
    )
    terminal = (
        RecursiveAtomCalculusTerminal.RECURSIVE_ATOM_STUDY_CALCULUS_FROZEN
        if all_checks_passed
        else RecursiveAtomCalculusTerminal.CANNOT_CHECK
    )

    payload = {
        "version": "RecursiveAtomCalculusClosureReport.v1",
        "candidate_coordinate_count": coordinate_count,
        "candidate_transformation_count": transform_count,
        "existing_owner_count": existing_count,
        "generic_new_atoms_claimed": generic_claimed,
        "ownership_missing_rows": list(missing_rows),
        "post_map_round_count": len(_POST_MAP_ROUNDS),
        "post_map_material_change_round_ids": sorted(material_change_round_ids),
        "common_result_disposition_count": len(tuple(AtomStudyDisposition)),
        "recursion_stop_reason_count": len(tuple(RecursionStopReason)),
        "negative_history_category_count": len(tuple(NegativeHistoryCategory)),
        "interaction_witness_count": len(_INTERACTION_WITNESSES),
        "interaction_mismatched_case_ids": sorted(mismatched),
        "terminal": terminal.value,
        "all_checks_passed": all_checks_passed,
        "grants_scientific_atom_authority": False,
        "grants_jump_authority": False,
        "grants_novelty_authority": False,
        "grants_issue_closure_authority": False,
    }
    report = RecursiveAtomCalculusClosureReport(
        candidate_coordinate_count=payload["candidate_coordinate_count"],
        candidate_transformation_count=payload["candidate_transformation_count"],
        existing_owner_count=payload["existing_owner_count"],
        generic_new_atoms_claimed=payload["generic_new_atoms_claimed"],
        ownership_missing_rows=tuple(payload["ownership_missing_rows"]),
        post_map_round_count=payload["post_map_round_count"],
        post_map_material_change_round_ids=tuple(
            payload["post_map_material_change_round_ids"]
        ),
        common_result_disposition_count=payload["common_result_disposition_count"],
        recursion_stop_reason_count=payload["recursion_stop_reason_count"],
        negative_history_category_count=payload["negative_history_category_count"],
        interaction_witness_count=payload["interaction_witness_count"],
        interaction_mismatched_case_ids=tuple(payload["interaction_mismatched_case_ids"]),
        terminal=RecursiveAtomCalculusTerminal(payload["terminal"]),
        all_checks_passed=payload["all_checks_passed"],
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "AtomStudyDisposition",
    "InteractionWitnessCase",
    "NegativeHistoryCategory",
    "PostMapSaturationRound",
    "RecursionStopReason",
    "RecursiveAtomCalculusClosureReport",
    "RecursiveAtomCalculusTerminal",
    "build_recursive_atom_calculus_closure_report",
    "classify_interaction_witness",
    "common_result_dispositions",
    "interaction_witness_cases",
    "negative_history_categories",
    "post_map_saturation_rounds",
    "recursion_stop_reasons",
]
